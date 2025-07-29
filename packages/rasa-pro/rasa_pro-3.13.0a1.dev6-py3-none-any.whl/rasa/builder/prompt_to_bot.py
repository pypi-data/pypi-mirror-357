import asyncio
import collections
import importlib
import json
import logging
import sys
import tempfile
import traceback
from copy import deepcopy
from textwrap import dedent
from typing import Any, Callable, Dict, List, Optional

import importlib_resources
import openai
import structlog
from jinja2 import Template
from pydantic import BaseModel
from sanic import Sanic, response
from structlog.testing import capture_logs

import rasa.core.utils
from rasa.builder.llm_context import tracker_as_llm_context
from rasa.cli.utils import validate_files
from rasa.constants import PACKAGE_NAME
from rasa.core import agent, channels
from rasa.core.channels.channel import InputChannel
from rasa.core.channels.studio_chat import StudioChatInput
from rasa.core.utils import AvailableEndpoints, read_endpoints_from_path
from rasa.model_training import train
from rasa.server import configure_cors
from rasa.shared.constants import DOMAIN_SCHEMA_FILE, RESPONSES_SCHEMA_FILE
from rasa.shared.core.domain import Domain
from rasa.shared.core.flows.yaml_flows_io import FLOWS_SCHEMA_FILE, YAMLFlowsReader
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.shared.importers.importer import TrainingDataImporter
from rasa.shared.importers.static import StaticTrainingDataImporter
from rasa.shared.utils.io import read_json_file
from rasa.shared.utils.yaml import (
    dump_obj_as_yaml_to_string,
    read_schema_file,
    read_yaml,
    read_yaml_file,
)
from rasa.utils.common import configure_logging_and_warnings
from rasa.utils.log_utils import configure_structlog
from rasa.utils.sanic_error_handler import register_custom_sanic_error_handler

structlogger = structlog.get_logger()

DEFAULT_SKILL_GENERATION_SYSTEM_PROMPT = importlib.resources.read_text(
    "rasa.builder",
    "skill_to_bot_prompt.jinja2",
)

DEFAULT_LLM_HELPER_SYSTEM_PROMPT = importlib.resources.read_text(
    "rasa.builder",
    "llm_helper_prompt.jinja2",
)

VECTOR_STORE_ID = "vs_685123376e288191a005b6b144d3026f"


default_credentials_yaml = """
studio_chat:
  user_message_evt: "user_message"
  bot_message_evt: "bot_message"
  session_persistence: true
"""

# create a dict where we collect most recent logs. only collect the last 30 log lines
# use a builtin type for this
recent_logs = collections.deque(maxlen=30)


def collecting_logs_processor(logger, log_level, event_dict):
    if log_level != logging.getLevelName(logging.DEBUG).lower():
        event_message = event_dict.get("event_info") or event_dict.get("event", "")
        recent_logs.append(f"[{log_level}] {event_message}")

    return event_dict


class PromptRequest(BaseModel):
    prompt: str
    client_id: Optional[str] = None


def default_credentials() -> Dict[str, Any]:
    return read_yaml(default_credentials_yaml)


def default_endpoints() -> Dict[str, Any]:
    return read_yaml_file(
        str(
            importlib_resources.files(PACKAGE_NAME).joinpath(
                "cli/project_templates/default/endpoints.yml"
            )
        )
    )


def default_config(assistant_id: str) -> Dict[str, Any]:
    base_config = read_yaml_file(
        str(
            importlib_resources.files(PACKAGE_NAME).joinpath(
                "cli/project_templates/default/config.yml"
            )
        )
    )

    base_config["assistant_id"] = assistant_id

    return base_config


async def continuously_run_task(task: Callable, name: str) -> None:
    """Regularly run a task."""
    structlogger.debug("prompt_to_bot.continuously_run_task.started", name=name)

    while True:
        try:
            if asyncio.iscoroutinefunction(task):
                await task()
            else:
                task()
        except asyncio.exceptions.CancelledError:
            structlogger.debug(
                "prompt_to_bot.continuously_run_task.cancelled", name=name
            )
            break
        except Exception as e:
            structlogger.error(
                "prompt_to_bot.continuously_run_task.error", name=name, error=str(e)
            )
        finally:
            await asyncio.sleep(0.1)


class PromptToBotService:
    def __init__(self):
        self.app = Sanic("PromptToBotService")
        self.app.ctx.agent = None
        self.input_channel = self.setup_input_channel()
        self.setup_routes(self.input_channel)
        self.max_retries = 5
        self.bot_files = {}

        configure_cors(self.app, cors_origins=["*"])

    def setup_input_channel(self) -> StudioChatInput:
        studio_chat_credentials = default_credentials().get(StudioChatInput.name())
        return StudioChatInput.from_credentials(credentials=studio_chat_credentials)

    def setup_routes(self, input_channel: InputChannel):
        self.app.add_route(
            self.handle_prompt_to_bot, "/api/prompt-to-bot", methods=["POST"]
        )
        self.app.add_route(self.get_bot_data, "/api/bot-data", methods=["GET"])

        self.app.add_route(self.update_bot_data, "/api/bot-data", methods=["PUT"])

        self.app.add_route(self.llm_builder, "/api/llm-builder", methods=["POST"])

        self.app.add_route(self.health, "/", methods=["GET"])

        input_channels = [input_channel]
        channels.channel.register(input_channels, self.app, route="/webhooks/")

    def health(self, request):
        return response.json({"status": "ok"})

    def importer_for_data(self) -> TrainingDataImporter:
        return TrainingDataImporter.wrap_in_builtins(
            [
                StaticTrainingDataImporter(
                    domain=Domain.from_dict(
                        read_yaml(self.bot_files.get("domain.yml", ""))
                    ),
                    flows=YAMLFlowsReader.read_from_string(
                        self.bot_files.get("flows.yml", "")
                    ),
                    config=self.config_from_bot_data(),
                )
            ]
        )

    async def validate_rasa_project(self) -> Optional[str]:
        """Validate the Rasa project data."""
        was_sys_exit_called = {"value": False}

        def sys_exit_mock(code: int = 0):
            was_sys_exit_called["value"] = True

        # prevent sys.exit from being called
        original_exit = sys.exit
        # TODO: avoid sys exit in the validation functions in the first place
        sys.exit = sys_exit_mock
        try:
            training_data_importer = self.importer_for_data()

            with capture_logs() as cap_logs:
                validate_files(
                    fail_on_warnings=False,
                    max_history=None,
                    importer=training_data_importer,
                )

            if was_sys_exit_called["value"]:
                structlogger.error(
                    "prompt_to_bot.validate_rasa_project.failed.sys_exit",
                    error_logs=cap_logs,
                )
                return json.dumps(
                    [x for x in cap_logs if x.get("log_level") != "debug"]
                )

            return None
        except Exception as e:
            structlogger.error(
                "prompt_to_bot.validate_rasa_project.failed.exception",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return str(e)
        finally:
            sys.exit = original_exit

    async def handle_prompt_to_bot(self, request):
        try:
            prompt_data = PromptRequest(**request.json)
            config = default_config(prompt_data.client_id)
            # Generate Rasa project data with retries
            await self.generate_rasa_project_with_retries(
                prompt_data.prompt,
                config,
                self.max_retries,
            )

            self.app.ctx.agent = await self.train_and_load_agent()

            return response.json(
                {
                    "bot_data": self.bot_files,
                    "status": "success",
                }
            )

        except Exception as e:
            structlogger.error("prompt_to_bot.error", error=str(e))
            return response.json({"error": str(e)}, status=500)

    async def get_bot_data(self, request):
        return response.json(self.bot_files)

    async def update_bot_data(self, request):
        response = await request.respond(content_type="text/event-stream")

        def sse_event(event, data):
            return f"event: {event}\ndata: {json.dumps(data)}\n\n"

        # 1. Received
        await response.send(sse_event("received", {"status": "received"}))

        bot_data = request.json
        for file_name, file_content in bot_data.items():
            self.bot_files[file_name] = file_content

        # 2. Validating
        await response.send(sse_event("validating", {"status": "validating"}))
        try:
            await self.validate_rasa_project()
            await response.send(
                sse_event("validation_success", {"status": "validation_success"})
            )
        except Exception as e:
            structlogger.error(
                "prompt_to_bot.update_bot_data.validation_error",
                error=str(e),
                event_info="Failed to validate the Rasa project. Error: " + str(e),
            )
            await response.send(
                sse_event(
                    "validation_error",
                    {"status": "validation_error", "error": str(e)},
                )
            )
            await response.eof()
            return

        # 3. Training
        await response.send(sse_event("training", {"status": "training"}))
        try:
            self.app.ctx.agent = await self.train_and_load_agent()
            await response.send(sse_event("train_success", {"status": "train_success"}))
        except Exception as e:
            structlogger.error(
                "prompt_to_bot.update_bot_data.train_error",
                error=str(e),
                event_info="Failed to train the agent. Error: " + str(e),
            )
            await response.send(
                sse_event("train_error", {"status": "train_error", "error": str(e)})
            )
            await response.eof()
            return

        # 4. Done
        await response.send(
            sse_event("done", {"status": "done", "bot_data": self.bot_files})
        )
        await response.eof()

    def config_from_bot_data(self) -> Dict[str, Any]:
        return read_yaml(self.bot_files.get("config.yml", ""))

    def update_stored_bot_data(self, bot_data: Dict[str, Any], config: Dict[str, Any]):
        self.bot_files = {
            "domain.yml": dump_obj_as_yaml_to_string(bot_data["domain"]),
            "flows.yml": dump_obj_as_yaml_to_string(bot_data["flows"]),
            "config.yml": dump_obj_as_yaml_to_string(config),
        }

    async def generate_rasa_project_with_retries(
        self, skill_description: str, config: Dict[str, Any], max_retry_count: int = 5
    ) -> Dict[str, Any]:
        """Generate Rasa project data with retry logic."""
        initial_messages = self.prompt_messages(skill_description)

        async def _generate(messages: List[Dict[str, Any]], tries_left: int):
            rasa_project_data = await self.generate_rasa_project(messages)
            self.update_stored_bot_data(rasa_project_data, config)

            structlogger.info(
                "prompt_to_bot.generate_rasa_project_with_retries.generated_project",
                tries_left=tries_left,
            )

            try:
                validation_error = await self.validate_rasa_project()

                if validation_error:
                    structlogger.error(
                        "prompt_to_bot.generate_rasa_project_with_retries.validation_error",
                        validation_error=validation_error,
                    )
                    raise Exception(validation_error)

                structlogger.info(
                    "prompt_to_bot.generate_rasa_project_with_retries.validation_success",
                    tries_left=tries_left,
                )

                return rasa_project_data
            except Exception as e:
                structlogger.error(
                    "prompt_to_bot.generate_rasa_project_with_retries.error",
                    error=str(e),
                    tries_left=tries_left,
                )

                if tries_left <= 0:
                    raise Exception(
                        f"Failed to generate valid Rasa project after "
                        f"{max_retry_count} attempts"
                    )

                # Use error to improve the prompt
                messages = messages + [
                    {
                        "role": "assistant",
                        "content": json.dumps(rasa_project_data),
                    },
                    {
                        "role": "user",
                        "content": dedent(f"""
                      Previous attempt failed with error: {e!s}

                      Please fix the issues and generate a valid Rasa project.
                    """),
                    },
                ]

                return await _generate(messages, tries_left - 1)

        return await _generate(initial_messages, max_retry_count)

    def prompt_messages(self, skill_description: str) -> List[Dict[str, Any]]:
        system_prompt = Template(DEFAULT_SKILL_GENERATION_SYSTEM_PROMPT).render(
            skill_description=skill_description
        )

        return [
            {"role": "system", "content": system_prompt},
        ]

    async def generate_rasa_project(
        self, messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate Rasa project data using LLM."""
        schema_file = str(
            importlib_resources.files(PACKAGE_NAME).joinpath(FLOWS_SCHEMA_FILE)
        )

        # TODO: clean up the schema
        flows_schema = deepcopy(read_json_file(schema_file))

        del flows_schema["$defs"]["flow"]["properties"]["nlu_trigger"]

        # TODO: restrict the domain schema to only the properties that are
        # needed for the CALM bot
        domain_schema = deepcopy(
            read_schema_file(DOMAIN_SCHEMA_FILE, PACKAGE_NAME, False)
        )

        # not needed in calm
        del domain_schema["mapping"]["intents"]
        del domain_schema["mapping"]["entities"]
        del domain_schema["mapping"]["forms"]

        # don't think the llm needs to configure these
        del domain_schema["mapping"]["config"]
        del domain_schema["mapping"]["session_config"]

        # don't work, llm tends to pick from_intent or something like that
        del domain_schema["mapping"]["slots"]["mapping"]["regex;([A-Za-z]+)"][
            "mapping"
        ]["mappings"]
        # also creates issues...
        del domain_schema["mapping"]["slots"]["mapping"]["regex;([A-Za-z]+)"][
            "mapping"
        ]["validation"]

        # pull in the responses schema
        domain_schema["mapping"]["responses"] = read_schema_file(
            RESPONSES_SCHEMA_FILE, PACKAGE_NAME, False
        )["schema;responses"]

        client = openai.AsyncOpenAI()
        response = await client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=messages,
            temperature=0.7,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "rasa_project",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "domain": domain_schema,
                            "flows": flows_schema,
                        },
                        "required": ["domain", "flows"],
                    },
                },
            },
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            raise Exception("LLM response was not valid JSON")

    async def generate_chat_bot_context(self) -> str:
        """Generate a chat bot context."""
        if self.app.ctx.agent and self.input_channel.latest_tracker_session_id:
            tracker: Optional[
                DialogueStateTracker
            ] = await self.app.ctx.agent.tracker_store.retrieve(
                self.input_channel.latest_tracker_session_id
            )
            return tracker_as_llm_context(tracker)
        else:
            return tracker_as_llm_context(None)

    def format_chat_dump(self, user_chat_history: List[Dict[str, Any]]) -> str:
        """Format the chat dump for the LLM."""
        result = ""
        for message in user_chat_history:
            if message.get("type") == "user":
                result += f"User: {message.get('content')}\n"
            else:
                for part in message.get("content", []):
                    if part.get("type") == "text":
                        result += f"Assistant: {part.get('text')}\n"
        return result

    def llm_helper_prompt_messages(
        self,
        current_conversation: str,
        bot_logs: str,
        chat_bot_files: Dict[str, str],
        documentation_results: str,
    ) -> List[Dict[str, Any]]:
        system_prompt = Template(DEFAULT_LLM_HELPER_SYSTEM_PROMPT).render(
            current_conversation=current_conversation,
            bot_logs=bot_logs,
            chat_bot_files=chat_bot_files,
            documentation_results=documentation_results,
        )

        return [
            {"role": "system", "content": system_prompt},
        ]

    async def llm_builder(self, request):
        current_conversation = await self.generate_chat_bot_context()
        bot_logs = "\n".join(recent_logs)
        chat_bot_files = self.bot_files
        user_chat_history = request.json.get("messages", [])
        chat_dump = self.format_chat_dump(user_chat_history)

        client = openai.AsyncOpenAI()

        results = await client.vector_stores.search(
            vector_store_id=VECTOR_STORE_ID,
            query=chat_dump,
            max_num_results=10,
            rewrite_query=True,
        )

        documentation_results = self.format_results(results.data)

        messages = self.llm_helper_prompt_messages(
            current_conversation,
            bot_logs,
            chat_bot_files,
            documentation_results,
        )

        for message in user_chat_history:
            messages.append(
                {
                    "role": "user" if message.get("type") == "user" else "assistant",
                    "content": json.dumps(message.get("content")),
                }
            )

        llm_helper_schema = read_json_file(
            importlib_resources.files(PACKAGE_NAME).joinpath(
                "builder/llm-helper-schema.json"
            )
        )

        openai_response = await client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "llm_helper",
                    "schema": llm_helper_schema,
                },
            },
        )

        return response.json(json.loads(openai_response.choices[0].message.content))

    @staticmethod
    def format_results(results):
        formatted_results = ""
        for result in results:
            formatted_result = f"<result url='{result.attributes.get('url')}'>"
            for part in result.content:
                formatted_result += f"<content>{part.text}</content>"
            formatted_results += formatted_result + "</result>"
        return f"<sources>{formatted_results}</sources>"

    async def train_and_load_agent(self):
        file_importer = self.importer_for_data()
        # this is used inside the training validation. validation assumes
        # that the endpoints are either stored in the default location or
        # that they have been loaded before - so that is what we do here.
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(
                dump_obj_as_yaml_to_string(default_endpoints()).encode("utf-8")
            )
            temp_file.flush()
            AvailableEndpoints.reset_instance()
            read_endpoints_from_path(temp_file.name)

        available_endpoints = AvailableEndpoints.get_instance()
        assert available_endpoints is not None

        training_result = await train(
            domain="",
            config="",
            training_files=None,
            file_importer=file_importer,
        )

        structlogger.info(
            "prompt_to_bot.train_and_load_agent.training_result",
            training_result=training_result,
        )

        agent_instance = await agent.load_agent(
            model_path=training_result.model,
            remote_storage=None,
            endpoints=available_endpoints,
            loop=self.app.loop,
        )

        structlogger.info(
            "prompt_to_bot.train_and_load_agent.agent_instance",
            agent_instance=agent_instance,
        )

        if not agent_instance.is_ready():
            raise Exception(
                "Generation of the chatbot failed with an error (model failed "
                "to load). Please try again."
            )

        structlogger.info(
            "prompt_to_bot.train_and_load_agent.agent_ready",
            agent_instance=agent_instance,
        )

        self.input_channel.agent = agent_instance
        return agent_instance


def main():
    """Start the Prompt to Bot service."""
    log_level = logging.DEBUG
    configure_logging_and_warnings(
        log_level=log_level,
        logging_config_file=None,
        warn_only_once=True,
        filter_repeated_logs=True,
    )
    configure_structlog(
        log_level,
        include_time=True,
        additional_processors=[
            collecting_logs_processor,
        ],
    )

    service = PromptToBotService()
    register_custom_sanic_error_handler(service.app)

    rasa.core.utils.list_routes(service.app)

    service.app.run(host="0.0.0.0", port=5005, legacy=True, motd=False)


if __name__ == "__main__":
    main()

from shiny import (
    App,
    Inputs,
    Outputs,
    Session,
    render,
    ui,
    reactive,
    module,
    render,
    run_app,
)
from agno.run.response import RunEvent, RunResponse

from utils import logger
from utils import get_model
from utils import get_agent
import os
import argparse
import json
from pathlib import Path

# turn off telemetry
os.environ["AGNO_TELEMETRY"] = "false"


# utility to stream agno run responses to shiny
def as_stream(response):
    for chunk in response:
        if isinstance(chunk, RunResponse) and isinstance(chunk.content, str):
            if chunk.event == RunEvent.run_response:
                yield chunk.content


## chat module ##
@module.ui
def chat_mod_ui(messages=[]):
    if messages:
        # filter out the system messages (not done for some reason in a module)
        logger.debug(messages)
        messages = [m for m in messages if m["role"] in ["user", "assistant"]]
        chat_ui = ui.chat_ui(id="chat", messages=messages, height="80vh", fill=True)
    else:
        chat_ui = ui.chat_ui(id="chat", height="80vh", width="80vw", fill=True)
    return chat_ui


@module.server
def chat_mod_server(input, output, session, messages):

    # pull in our environment variables for configuration
    logger.debug(f"ENVIRON: {os.environ["_ILLUMINAITE_CONFIG"]}")
    config = json.loads(os.environ["_ILLUMINAITE_CONFIG"])
    logger.info(f"{config['provider']} {config['model_name']}")
    model_choice = get_model(config["provider"], config["model_name"])
    agent = get_agent(model_choice=model_choice)
    chat = ui.Chat(id="chat", messages=messages)

    @chat.on_user_submit
    async def _():
        new_message = chat.user_input()
        chunks = agent.run(message=new_message, stream=True)
        await chat.append_message_stream(as_stream(chunks))


## end chat module


# page layout
app_page_chat_ui = ui.page_fluid(
    ui.card(
        ui.card_header("IlluminAIte"),
        ui.output_ui("chat"),
    ),
)


# page logic
def agno_chat_server(input: Inputs, output: Outputs, session: Session):

    @render.ui
    def chat():

        chat_messages = []
        # start the module server
        chat_mod_server("chat_session", messages=chat_messages)
        # start the module UI
        return chat_mod_ui("chat_session", messages=chat_messages)


def main():
    parser = argparse.ArgumentParser(
        description="illuminAIte - AI-powered data conversation tool"
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "google", "ollama"],
        default="google",
        help="Choose the AI provider (openai, google, ollama)",
    )
    parser.add_argument(
        "--model-name",
        help="Specify the model name/id (e.g. gpt-4, gemini-1.5-pro, llama2)",
        default="gemini-1.5-flash",
    )
    # since this gets run by the shiny app, we need to pass the args as env vars
    config = parser.parse_args()
    logger.debug(f"Starting illuminAIte with config: {config}")
    os.environ["_ILLUMINAITE_CONFIG"] = json.dumps(vars(config))

    run_app(
        "illuminAIte:starlette_app",
        launch_browser=True,
        log_level="debug",
        reload=True,
    )


# allow this to run standalone
starlette_app = App(app_page_chat_ui, agno_chat_server)
if __name__ == "__main__":
    main()

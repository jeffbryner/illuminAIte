from shiny import (
    App,
    run_app,
)
from app.utils import logger
from app.chat import agno_chat_server, app_page_chat_ui
import os
import argparse
import json


# turn off telemetry
os.environ["AGNO_TELEMETRY"] = "false"


def main():
    parser = argparse.ArgumentParser(
        description="illuminAIte - AI-powered data conversation"
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "google", "ollama"],
        default="google",
        help="Choose the AI provider (openai, google, ollama)",
    )
    parser.add_argument(
        "--model-name",
        help="Specify the model name/id (e.g. gpt-4, gemini-2.0-flash, llama2)",
        default="gemini-1.5-flash",
    )
    parser.add_argument(
        "--location",
        help="Specify the GCP location (e.g. us-central1)",
        default="us-central1",
    )

    # since this gets run by the shiny app, we need to pass the args as env vars
    config = parser.parse_args()
    logger.debug(f"Starting illuminAIte with config: {config}")
    os.environ["_ILLUMINAITE_CONFIG"] = json.dumps(vars(config))

    run_app(
        "illuminAIte:starlette_app",
        launch_browser=True,
        log_level="info",
        reload=True,
    )


# allow this to run standalone
starlette_app = App(app_page_chat_ui, agno_chat_server)
if __name__ == "__main__":
    main()

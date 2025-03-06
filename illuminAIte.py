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
from agno.agent import Agent, AgentMemory
from agno.run.response import RunEvent, RunResponse
from agno.memory.classifier import MemoryClassifier
from agno.memory.summarizer import MemorySummarizer
from agno.memory.manager import MemoryManager
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.memory.db.sqlite import SqliteMemoryDb

from gemini_models import model_flash, model_pro

# from agno.models.openai import OpenAIChat

# from agno.tools.duckduckgo import DuckDuckGoTools
from turbo_duck_tools import TurboDuckTools
from agno.tools.file import FileTools
from agno.tools.duckdb import DuckDbTools
from utils import logger
import os
from pathlib import Path

# turn off telemetry
os.environ["AGNO_TELEMETRY"] = "false"

agent_storage: str = "tmp/agent_storage.db"
agent_memory: str = "tmp/agent_memory.db"
agent_database: str = "tmp/agent_database.db"
# https://duckdb.org/docs/stable/configuration/overview.html#configuration-reference
duckdb_config = {"external_threads": 1}

# model_choice = OpenAIChat(id="gpt-4o")
model_choice = model_flash

agent = Agent(
    model=model_choice,
    tools=[
        FileTools(save_files=False, read_files=False),
        DuckDbTools(db_path=agent_database, config=duckdb_config),
        TurboDuckTools(),
    ],
    session_id="csv_chat_agent",
    session_name="csv_chat_agent",
    user_id="csv_chat_user",
    markdown=True,
    show_tool_calls=True,
    telemetry=False,
    monitoring=False,
    instructions=[
        "You have a set of local csv and json files to answer questions about.",
        "Use your file tools to list ONLY .csv or .json files. Never list other files."
        "Get a list of files yourself before asking for a filename",
        "You can then use duckdb tools to open the csv files and create a table and describe it for context on the data",
        "Use your duckdb tools analyze and answer questions",
        "Pay attention to columns with special characters or spaces since they will need to be quoted when accessing.",
        "You can then use duckdb to answer questions",
        "You can also search the internet with DuckDuckGo.",
        "Never send the local files to the internet, or to the AI model directly.",
    ],
    description="You are an expert in computer security and data analysis.",
    storage=SqliteAgentStorage(table_name="csv_chat_agent", db_file=agent_storage),
    # Adds the current date and time to the instructions
    add_datetime_to_instructions=True,
    # Adds the history of the conversation to the messages
    add_history_to_messages=True,
    # Number of history responses to add to the messages
    num_history_responses=50,
    memory=AgentMemory(
        db=SqliteMemoryDb(db_file=agent_memory),
        create_user_memories=True,
        create_session_summary=True,
        update_user_memories_after_run=True,
        update_session_summary_after_run=True,
        classifier=MemoryClassifier(model=model_choice),
        summarizer=MemorySummarizer(model=model_choice),
        manager=MemoryManager(model=model_choice),
    ),
)


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
        logger.info(messages)
        messages = [m for m in messages if m["role"] in ["user", "assistant"]]
        chat_ui = ui.chat_ui(id="chat", messages=messages, height="80vh", fill=True)
    else:
        chat_ui = ui.chat_ui(id="chat", height="80vh", width="80vw", fill=True)
    return chat_ui


@module.server
def chat_mod_server(input, output, session, messages):
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


# allow this to run standalone
starlette_app = App(app_page_chat_ui, agno_chat_server)
if __name__ == "__main__":

    run_app(
        "illuminAIte:starlette_app",
        launch_browser=True,
        log_level="debug",
        reload=True,
    )

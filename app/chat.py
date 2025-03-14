from shiny import (
    Inputs,
    Outputs,
    Session,
    render,
    ui,
    reactive,
    module,
    render,
)

from .utils import logger
from .utils import get_model
from .utils import get_agent
from .utils import as_stream
from .module_dataframe import dataframe_display_mod_ui, dataframe_display_mod_server
from .module_plotly import plotly_mod_ui, plotly_mod_server
from .module_matplot import plot_mod_ui, plot_mod_server
import os
import json
import uuid
import pandas
import re


## chat module ##
@module.ui
def chat_mod_ui(messages=[]):
    return (
        ui.chat_ui(
            id="chat", messages=messages, height="80vh", width="100%", fill=True
        ),
    )


@module.server
def chat_mod_server(input, output, session, messages):
    # setup our state to hold reactive values
    # and values that are shared across modules, tools, etc
    state = session.app.starlette_app.state
    state.dataframe = reactive.value(pandas.DataFrame())

    # pull in our environment variables for configuration
    logger.debug(f"ENVIRON: {os.environ["_ILLUMINAITE_CONFIG"]}")
    config = json.loads(os.environ["_ILLUMINAITE_CONFIG"])
    logger.info(f"{config['provider']} {config['model_name']}")
    state.model_choice = get_model(config["provider"], config["model_name"])
    agent = get_agent(model_choice=state.model_choice, state=state)

    chat = ui.Chat(id="chat", messages=messages)

    @chat.on_user_submit
    async def _():
        new_message = chat.user_input()
        # check for special messages
        if re.search(r"(show|display) (dataframe|datagrid|grid)", new_message.lower()):
            if len(state.dataframe()) > 0:
                # Create unique ID for each dataframe display instance
                display_id = f"dataframe_display_{uuid.uuid4().hex}"
                await chat.append_message(
                    ui.TagList(dataframe_display_mod_ui(display_id))
                )
                # Initialize the module server with unique ID and unique dataframe
                grid_dataframe = state.dataframe.get().copy()
                dataframe_display_mod_server(display_id, dataframe=grid_dataframe)
                return
            else:
                await chat.append_message(
                    "no dataframe to show, try instructing the agent to load data into the dataframe"
                )
                return

        if re.search(r"(show|display) matplot", new_message.lower()):
            if len(state.dataframe()) > 0:
                # Create unique ID for each plot display instance
                display_id = f"plot_display_{uuid.uuid4().hex}"
                await chat.append_message(ui.TagList(plot_mod_ui(display_id)))
                # Initialize the module server with unique ID and unique dataframe
                plot_dataframe = state.dataframe.get().copy()

                plot_mod_server(display_id, dataframe=plot_dataframe)
                return
            else:
                await chat.append_message(
                    "no dataframe to plot, try instructing the agent to load data into the dataframe"
                )
                return
        if re.search(r"(show|display) (graph|plot|plotly)", new_message.lower()):
            if len(state.dataframe()) > 0:
                # Create unique ID for each plot display instance
                display_id = f"plotly_display_{uuid.uuid4().hex}"
                logger.info(f"plotly display id: {display_id}")
                await chat.append_message(
                    ui.TagList(plotly_mod_ui(display_id)),
                )
                # Initialize the module server with unique ID and unique dataframe
                plot_dataframe = state.dataframe.get().copy()
                plotly_mod_server(display_id, dataframe=plot_dataframe)
                return
            else:
                await chat.append_message(
                    "no dataframe to plot, try instructing the agent to load data into the dataframe"
                )
                return

        # else let the agent handle the response
        chunks = agent.run(message=new_message, stream=True)
        await chat.append_message_stream(as_stream(chunks))

    # @reactive.effect
    # async def dataframe_changed():
    #     state.dataframe()
    #     logger.info(f"dataframe changed: {state.dataframe()}")


## end chat module


# page layout
app_page_chat_ui = ui.page_fluid(
    ui.card(
        ui.card_header("illuminAIte - AI-powered data conversation"),
        ui.output_ui("chat"),
    ),
)


# page logic
def agno_chat_server(input: Inputs, output: Outputs, session: Session):

    @render.ui
    def chat():

        chat_messages = [
            ui.TagList(
                ui.span("what data can we chat about?")
                .add_class("suggestion")
                .add_class("submit")
            ),
        ]
        # start the module server
        chat_mod_server("chat_session", messages=chat_messages)
        # start the module UI
        return chat_mod_ui("chat_session", messages=chat_messages)

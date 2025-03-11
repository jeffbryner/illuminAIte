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
from shiny.express import ui as x_ui
from shiny.express import module as x_module
from shinywidgets import output_widget, render_widget, render_plotly


from utils import logger
from utils import get_model
from utils import get_agent
from utils import as_stream
import os
import argparse
import json
from pathlib import Path
import pandas
import random
from htmltools import HTML
import matplotlib.pyplot as plt
import uuid


# turn off telemetry
os.environ["AGNO_TELEMETRY"] = "false"


## matplot module ##
@module.ui
def plot_mod_ui():
    return ui.card(
        ui.accordion(
            ui.accordion_panel(
                "Plot",
                ui.div(
                    ui.input_select(
                        "plot_type",
                        "Select Plot Type",
                        choices=["scatter", "line", "bar", "boxplot"],
                        width="100%",
                    ),
                    ui.row(
                        ui.column(
                            6,
                            ui.input_selectize(
                                "x_var",
                                "X Variable",
                                choices=[],
                                multiple=False,
                                width="100%",
                            ),
                        ),
                        ui.column(
                            6,
                            ui.input_selectize(
                                "y_var",
                                "Y Variable",
                                choices=[],
                                multiple=False,
                                width="100%",
                            ),
                        ),
                    ),
                    ui.output_plot("plot"),
                ),
            )
        ),
        full_screen=True,
    )


@module.server
def plot_mod_server(input, output, session, dataframe):
    @reactive.effect
    def update_var_choices():
        choices = dataframe.columns.tolist()
        ui.update_selectize(
            "x_var", choices=choices, selected=choices[0] if choices else None
        )
        ui.update_selectize(
            "y_var", choices=choices, selected=choices[1] if len(choices) > 1 else None
        )

    @render.plot
    def plot():

        if not input.x_var() or not input.y_var():
            return None

        df = dataframe
        plot_type = input.plot_type()

        fig, ax = plt.subplots()

        if plot_type == "scatter":
            ax.scatter(df[input.x_var()], df[input.y_var()])
        elif plot_type == "line":
            ax.plot(df[input.x_var()], df[input.y_var()])
        elif plot_type == "bar":
            ax.bar(df[input.x_var()], df[input.y_var()])
        elif plot_type == "boxplot":
            ax.boxplot(df[input.y_var()], labels=[input.x_var()])

        ax.set_xlabel(input.x_var())
        ax.set_ylabel(input.y_var())
        plt.xticks(rotation=45)
        plt.tight_layout()

        return fig


## end matplot module ##


## plotly module ##
@module.ui
def plotly_mod_ui():
    return ui.card(
        ui.accordion(
            ui.accordion_panel(
                "Plotly Plot",
                ui.div(
                    ui.input_select(
                        "plotly_type",
                        "Select Plot Type",
                        choices=["scatter", "line", "histogram", "box"],
                        width="100%",
                    ),
                    ui.row(
                        ui.column(
                            6,
                            ui.input_selectize(
                                "px_x_var",
                                "X Variable",
                                choices=[],
                                multiple=False,
                                width="100%",
                            ),
                        ),
                        ui.column(
                            6,
                            ui.input_selectize(
                                "px_y_var",
                                "Y Variable",
                                choices=[],
                                multiple=False,
                                width="100%",
                            ),
                        ),
                    ),
                    output_widget("plotly_plot"),
                ),
            )
        ),
        full_screen=True,
    )


@module.server
def plotly_mod_server(input, output, session, dataframe):
    @reactive.effect
    def update_var_choices():
        choices = dataframe.columns.tolist()
        ui.update_selectize(
            "px_x_var", choices=choices, selected=choices[0] if choices else None
        )
        ui.update_selectize(
            "px_y_var",
            choices=choices,
            selected=choices[1] if len(choices) > 1 else None,
        )

    @render_widget
    def plotly_plot():
        import plotly.express as px

        if not input.px_x_var() or not input.px_y_var():
            return None

        df = dataframe
        plot_type = input.plotly_type()

        if plot_type == "scatter":
            fig = px.scatter(df, x=input.px_x_var(), y=input.px_y_var())
        elif plot_type == "line":
            fig = px.line(df, x=input.px_x_var(), y=input.px_y_var())
        elif plot_type == "histogram":
            fig = px.histogram(df, x=input.px_x_var())
        elif plot_type == "box":
            fig = px.box(df, x=input.px_x_var(), y=input.px_y_var())

        fig.update_layout(xaxis_title=input.px_x_var(), yaxis_title=input.px_y_var())

        return fig


## end plotly module ##


## dataframe module ##
@module.ui
def dataframe_display_mod_ui():
    return ui.div(ui.output_ui("summary_data_card"))


@module.server
def dataframe_display_mod_server(input, output, session, dataframe):
    @render.express
    def summary_data_card():
        with x_ui.card(full_screen=True):
            with x_ui.accordion():
                with x_ui.accordion_panel("DataFrame"):

                    @render.data_frame
                    def summary_data():
                        return render.DataGrid(
                            dataframe.round(2),
                        )


## end dataframe module ##


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
    state = session.app.starlette_app.state
    state.dataframe = reactive.value(pandas.DataFrame())

    # pull in our environment variables for configuration
    logger.debug(f"ENVIRON: {os.environ["_ILLUMINAITE_CONFIG"]}")
    config = json.loads(os.environ["_ILLUMINAITE_CONFIG"])
    logger.info(f"{config['provider']} {config['model_name']}")
    state.model_choice = get_model(config["provider"], config["model_name"])
    agent = get_agent(model_choice=state.model_choice, state=state)

    chat = ui.Chat(id="chat", messages=messages)

    # plot_mod_server("plot_session", dataframe=state.dataframe.get().copy())

    @chat.on_user_submit
    async def _():
        new_message = chat.user_input()
        # check for special messages
        if "show dataframe" in new_message.lower():
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

        if "show matplot" in new_message.lower():
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
        if "show plotly" in new_message.lower():
            if len(state.dataframe()) > 0:
                display_id = f"plotly_display_{uuid.uuid4().hex}"
                logger.info(f"plotly display id: {display_id}")
                await chat.append_message(
                    ui.TagList(plotly_mod_ui(display_id)),
                )
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

    @render.express
    def x_summary_data():
        with x_ui.card(height="400px"):

            @render.data_frame
            def summary_data():
                return render.DataGrid(
                    state.dataframe().round(2),
                )

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

        chat_messages = []
        # start the module server
        chat_mod_server("chat_session", messages=chat_messages)
        # start the module UI
        return chat_mod_ui("chat_session", messages=chat_messages)


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
        log_level="info",
        reload=True,
    )


# allow this to run standalone
starlette_app = App(app_page_chat_ui, agno_chat_server)
if __name__ == "__main__":
    main()

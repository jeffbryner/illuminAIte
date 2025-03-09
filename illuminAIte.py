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

# turn off telemetry
os.environ["AGNO_TELEMETRY"] = "false"


## plot module ##
@module.ui
def plot_mod_ui():
    return ui.div(
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
                    "x_var", "X Variable", choices=[], multiple=False, width="100%"
                ),
            ),
            ui.column(
                6,
                ui.input_selectize(
                    "y_var", "Y Variable", choices=[], multiple=False, width="100%"
                ),
            ),
        ),
        ui.output_plot("plot"),
    )


@module.server
def plot_mod_server(input, output, session, dataframe):
    @reactive.effect
    def update_var_choices():
        choices = dataframe().columns.tolist()
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

        df = dataframe()
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


## end plot module ##


## chat module ##
@module.ui
def chat_mod_ui(messages=[]):
    # if messages:
    #     # filter out the system messages (not done for some reason in a module)
    #     logger.debug(messages)
    #     messages = [m for m in messages if m["role"] in ["user", "assistant"]]
    #     chat_ui = ui.chat_ui(
    #         id="chat", messages=messages, height="80vh", width="80vw", fill=True
    #     )
    # else:
    #     messages = [
    #         ui.TagList(
    #             f"DataFrame:",
    #             ui.output_ui("x_summary_data"),
    #         ).get_html_string()
    #     ]
    #     chat_ui = ui.chat_ui(
    #         id="chat", messages=messages, height="80vh", width="80vw", fill=True
    #     )
    # return chat_ui
    return ui.row(
        ui.column(
            8,
            ui.chat_ui(
                id="chat", messages=messages, height="80vh", width="100%", fill=True
            ),
        ),
        ui.column(4, plot_mod_ui("plot_session")),
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

    # # Load the Gapminder dataset
    # df = px.data.gapminder()

    # # Prepare a summary DataFrame
    # summary_df = (
    #     df.groupby("country")
    #     .agg(
    #         {
    #             "pop": ["min", "max", "mean"],
    #             "lifeExp": ["min", "max", "mean"],
    #             "gdpPercap": ["min", "max", "mean"],
    #         }
    #     )
    #     .reset_index()
    # )

    # summary_df.columns = ["_".join(col).strip() for col in summary_df.columns.values]
    # summary_df.rename(columns={"country_": "country"}, inplace=True)
    # state.dataframe.set(summary_df)

    plot_mod_server("plot_session", dataframe=state.dataframe)

    @chat.on_user_submit
    async def _():
        new_message = chat.user_input()
        chunks = agent.run(message=new_message, stream=True)
        await chat.append_message_stream(as_stream(chunks))
        # await chat.append_message(
        #     ui.TagList(f"DataFrame:", ui.output_ui("x_summary_data"))
        # )
        # append a chart
        # fig = px.scatter([1, 2], [3, 4])
        # fig_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
        # logger.info(f"fig_html: {fig_html}")
        # logger.info(f"fig_html HTML: {ui.TagList(ui.HTML(fig_html)).get_html_string()}")
        # await chat.append_message(ui.TagList(ui.HTML(fig_html)).get_html_string())

        # # randomly sort the data to prove reactivity
        # column_choice = random.choice(state.dataframe.get().columns)
        # logger.info(f"sorting dataframe by: {column_choice}")
        # state.dataframe.set(state.dataframe().sort_values(column_choice))

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
        log_level="info",
        reload=True,
    )


# allow this to run standalone
starlette_app = App(app_page_chat_ui, agno_chat_server)
if __name__ == "__main__":
    main()

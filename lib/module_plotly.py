from shiny import (
    ui,
    reactive,
    module,
)
from shinywidgets import output_widget, render_widget
import plotly.express as px


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

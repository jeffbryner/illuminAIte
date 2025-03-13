from shiny import (
    render,
    ui,
    reactive,
    module,
    render,
)
import matplotlib.pyplot as plt


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

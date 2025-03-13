from shiny import (
    render,
    ui,
    module,
    render,
)
from shiny.express import ui as x_ui


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

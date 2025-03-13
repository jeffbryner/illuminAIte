from typing import Any, Dict, List, Optional, Tuple
from agno.tools import Toolkit
from .utils import logger
from .module_plotly import plotly_mod_ui, plotly_mod_server
from shiny import ui
import uuid
import asyncio
import concurrent.futures


# adds a tool to do dynamic plotting of dataframes


class PlotlyChartTools(Toolkit):
    def __init__(
        self,
        state=None,
    ):
        super().__init__(name="plotly_tools")

        # add our shiny state to the tools
        self.state = state
        self.pool = concurrent.futures.ThreadPoolExecutor()
        self.register(self.show_dynamic_chart)

    async def show_dynamic_chart(self) -> str:
        """
        Use this tool if asked to show a dynamic graph or chart based on the current data being discussed
        Be sure to load data relative to the discussion into the dynamic dataframe before calling this tool
        """
        #     return asyncio.run(self._async_show_dynamic_chart())
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.pool, self.async_show_dynamic_chart)

    async def async_show_dynamic_chart(self):
        """
        async method to call chat with the plotly chart

        :return: A description of the update to use in chat.
        """
        # logger.info(f"{self.state}")
        # we expect the chat component to be referenced in state
        if len(self.state.dataframe) > 0:
            # Create unique ID for each plot display instance
            display_id = f"plotly_display_{uuid.uuid4().hex}"
            logger.info(f"plotly display id: {display_id}")
            # await self.state.chat.append_message(
            #     ui.TagList(plotly_mod_ui(display_id)),
            # )
            # task = asyncio.create_task(
            #     self.state.chat.append_message(
            #         ui.TagList(f"plotly_mod_ui {display_id}")
            #     )
            # )
            # result = await task
            # logger.info(f"TASK result: {result}")
            # await self.state.chat.append_message([f"plotly_mod_ui {display_id}"])
            # Initialize the module server with unique ID and unique dataframe
            # plot_dataframe = self.state.dataframe.get().copy()
            # plotly_mod_server(display_id, dataframe=plot_dataframe)

        return []

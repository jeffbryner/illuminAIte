from typing import Any, Dict, List, Optional, Tuple
from agno.tools.duckdb import DuckDbTools
from agno.tools import Toolkit
from agno.utils.log import logger
import duckdb

# add some utility functions to the DuckDuckGoTools


class TurboDuckTools(DuckDbTools):
    def __init__(
        self,
        db_path: Optional[str] = None,
        connection: Optional[duckdb.DuckDBPyConnection] = None,
        init_commands: Optional[List] = None,
        read_only: bool = False,
        config: Optional[dict] = None,
        state=None,
    ):
        super().__init__(
            db_path=db_path,
            connection=connection,
            init_commands=init_commands,
            read_only=read_only,
            config=config,
        )
        # add our shiny state to the tools
        self.state = state
        self.register(self.load_dynamic_dataframe)
        self.register(self.load_local_json_to_table)

    def load_local_json_to_table(self, path: str, table: Optional[str]) -> str:
        """Load a local JSON file into duckdb

        :param path: Path to the json file
        :param table: Optional table name to use
        :return: Table name, SQL statement used to load the file
        """
        import os

        logger.debug(f"Loading {path} into duckdb")

        if table is None:
            # Get the file name from the path
            file_name = path.split("/")[-1]
            # Get the file name without extension from the s3 path
            table, extension = os.path.splitext(file_name)
            # If the table isn't a valid SQL identifier, we'll need to use something else
            table = (
                table.replace("-", "_")
                .replace(".", "_")
                .replace(" ", "_")
                .replace("/", "_")
            )

        select_statement = f"SELECT * FROM read_json('{path}')"

        create_statement = f"CREATE OR REPLACE TABLE '{table}' AS {select_statement};"
        self.run_query(create_statement)

        logger.debug(f"Loaded JSON {path} into duckdb as {table}")
        return create_statement

    def load_dynamic_dataframe(self, query: str) -> str:
        """Updates the dynamic dataframe with the results of a query

        :param query: Query to use to update the dataframe data, always use a limit of 1000 rows
        :return: A description of the update to use in chat.
        """
        # Execute query and update the reactive dataframe
        result_df = self.connection.sql(query).df()
        self.state.dataframe.set(result_df)

        return f"Dataframe data updated with {len(result_df)} rows from query: {query}"

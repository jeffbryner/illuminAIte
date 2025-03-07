from typing import Any, Dict, List, Optional, Tuple
from agno.tools.duckdb import DuckDbTools
from agno.tools import Toolkit
from agno.utils.log import logger

# add some utility functions to the DuckDuckGoTools


class TurboDuckTools(DuckDbTools):
    def load_local_json_to_table(
        self, path: str, table: Optional[str]
    ) -> Tuple[str, str]:
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

        select_statement = f"SELECT * FROM read_json('{path}'"

        create_statement = f"CREATE OR REPLACE TABLE '{table}' AS {select_statement};"
        self.run_query(create_statement)

        logger.debug(f"Loaded JSON {path} into duckdb as {table}")
        return table, create_statement

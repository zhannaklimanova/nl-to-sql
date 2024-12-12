import logging
import json
import re
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class QueryLoggingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        json_file = "nlq_sql.json"
        queries_file = "sql_queries.log"
        queries = []

        if connection.queries:
            with open(queries_file, "a") as log_file:
                for query in connection.queries:
                    log_file.write(query["sql"] + ";" + "\n")
                    sql = query["sql"] + ";"

                    cleaned_sql = sql.replace('"', "").strip()
                    logger.debug(f"{cleaned_sql}")

                    # Create the JSON entry, SQL in clean format for direct execution
                    entry = {
                        "nlq": "",
                        "sql": cleaned_sql,
                    }
                    queries.append(entry)

        # Write to the JSON file
        try:
            with open(json_file, "r") as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        existing_data.extend(queries)
        new_data = queries

        with open(json_file, "w") as f:
            json.dump(new_data, f, indent=4)

        return response

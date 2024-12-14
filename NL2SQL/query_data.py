from typing import Dict, Optional, List, Union


class PredictedQuery:
    def __init__(self, sql_query: str, predicted_output_path: str):
        self.sql_query = sql_query
        self.predicted_output_path = predicted_output_path

    @staticmethod
    def from_dict(data: Dict):
        return PredictedQuery(
            sql_query=data["sql_query"],
            predicted_output_path=data["predicted_output_path"],
        )


class PredictedSQLQueries:
    def __init__(
        self, gpt: PredictedQuery, claude: PredictedQuery, grok: PredictedQuery
    ):
        self.gpt = gpt
        self.claude = claude
        self.grok = grok

    @staticmethod
    def from_dict(data: Dict):
        return PredictedSQLQueries(
            gpt=PredictedQuery.from_dict(data["gpt"]),
            claude=PredictedQuery.from_dict(data["claude"]),
            grok=PredictedQuery.from_dict(data["grok"]),
        )


class QueryData:
    def __init__(
        self,
        sql_query: str,
        predicted_sql_query_without_options: PredictedSQLQueries,
        predicted_sql_query_with_options: PredictedSQLQueries,
        gold_output_path: str,
        natural_language_inputs: List[str],
    ):
        self.sql_query = sql_query
        self.predicted_sql_query_without_options = predicted_sql_query_without_options
        self.predicted_sql_query_with_options = predicted_sql_query_with_options
        self.gold_output_path = gold_output_path
        self.natural_language_inputs = natural_language_inputs

    @staticmethod
    def from_dict(data: Dict):
        return QueryData(
            sql_query=data["sql_query"],
            predicted_sql_query_without_options=PredictedSQLQueries.from_dict(
                data["predicted_sql_query_without_options"]
            ),
            predicted_sql_query_with_options=PredictedSQLQueries.from_dict(
                data["predicted_sql_query_with_options"]
            ),
            gold_output_path=data["gold_output_path"],
            natural_language_inputs=data["natural_language_inputs"],
        )

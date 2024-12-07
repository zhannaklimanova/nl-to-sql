import json
from typing import Dict
import pandas as pd


CHANTS_DATA_PATH = "data/chants_data.json"
FEASTS_DATA_PATH = "data/feasts_data.json"
SOURCES_DATA_PATH = "data/sources_data.json"


def evaluate(expected_data_path: str, actual_data_path: str, ordered=False) -> bool:
    expected_data: pd.DataFrame = pd.read_csv(expected_data_path)
    # For chants, the columns are renamed and the id column is always the first one
    try:
        expected_ids: pd.Series = expected_data["id"]
    except:
        expected_ids: pd.Series = expected_data["col1"]

    # If actual data does not load, that means the predicted SQL query did not work
    try:
        actual_data: pd.DataFrame = pd.read_csv(actual_data_path)
    except:
        return False

    # If id does not exist, then the data is wrong since all the gold outputs look for ids
    try:
        actual_ids: pd.Series = actual_data["id"]
    except:
        return False

    if not ordered:
        return (
            expected_ids.sort_values()
            .reset_index(drop=True)
            .equals(actual_ids.sort_values().reset_index(drop=True))
        )

    else:
        raise NotImplementedError("Have not implemented ordered evaluation yet")


def load_data_as_json(json_path: str) -> list[dict]:
    with open(json_path, "r") as file:
        return json.load(file)


class Paths:
    def __init__(self, expected: str, predicted: dict):
        self.expected: str = expected
        self.predicted = dict()
        for k, v in predicted.items():
            self.predicted[k] = v["predicted_output_path"]


def get_paths(item) -> Paths:
    return Paths(item["gold_output_path"], item["predicted_sql_query"])


if __name__ == "__main__":
    chants: list[dict] = load_data_as_json(CHANTS_DATA_PATH)
    data_paths = {
        "chants": CHANTS_DATA_PATH,
        "feasts": FEASTS_DATA_PATH,
        "sources": SOURCES_DATA_PATH,
    }
    all_counts = dict()

    for k in data_paths.keys():
        all_counts[k] = dict()

    for name, data_path in data_paths.items():
        data = load_data_as_json(data_path)
        counts = dict()
        for item in data:
            paths: Paths = get_paths(item)
            for llm, predicted_path in paths.predicted.items():
                if llm not in counts:
                    counts[llm] = 0
                actual_matches_expected: bool = evaluate(paths.expected, predicted_path)
                if actual_matches_expected:
                    counts[llm] += 1
        all_counts[name] = counts
    print(all_counts)

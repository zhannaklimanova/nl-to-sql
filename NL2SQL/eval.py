import json
from typing import Dict, List
import pandas as pd
from scipy.stats import spearmanr
from query_data import QueryData


CHANTS_DATA_PATH = "data/chants_data.json"
FEASTS_DATA_PATH = "data/feasts_data.json"
SOURCES_DATA_PATH = "data/sources_data.json"


class Paths:
    def __init__(
        self,
        expected: str,
        predicted_without_options: Dict[str, str],
        predicted_with_options: Dict[str, str],
    ):
        self.expected: str = expected
        self.predicted_without_options = predicted_without_options
        self.predicted_with_options = predicted_with_options


def load_data_as_json(json_path: str) -> List[QueryData]:
    with open(json_path, "r") as file:
        data = json.load(file)
    return [QueryData.from_dict(item) for item in data]


all_metrics = {
    "unordered": lambda expected_ids, actual_ids: expected_ids.sort_values()
    .reset_index(drop=True)
    .equals(actual_ids.sort_values().reset_index(drop=True)),
    "ordered": lambda expected_ids, actual_ids: expected_ids.equals(actual_ids),
    "extra_items": lambda expected_ids, actual_ids: len(
        set(actual_ids) - set(expected_ids)
    )
    / len(expected_ids),
    "missing_items": lambda expected_ids, actual_ids: len(
        set(expected_ids) - set(actual_ids)
    )
    / len(expected_ids),
    "intersection": lambda expected_ids, actual_ids: len(
        set(expected_ids).intersection(set(actual_ids))
    )
    / len(expected_ids),
}


def evaluate(
    expected_data_path: str, actual_data_path: str, metric="unordered"
) -> float:
    expected_data: pd.DataFrame = pd.read_csv(expected_data_path)
    actual_data: pd.DataFrame = pd.read_csv(actual_data_path)

    try:
        expected_ids = expected_data["id"]
    except KeyError:
        expected_ids = expected_data["col1"]

    try:
        actual_ids = actual_data["id"]
    except KeyError:
        return 0

    return all_metrics[metric](expected_ids, actual_ids)


def evaluate_data(data_path: str) -> Dict[str, Dict[str, Dict[str, int]]]:
    """
    Evaluate data from a given path and return counts for each metric, organized by
    "with_options" and "without_options".
    """
    data = load_data_as_json(data_path)
    metrics = list(all_metrics.keys())

    # Structure the result as a dictionary with categories for with_options and without_options
    results = {
        "with_options": {metric: {} for metric in metrics},
        "without_options": {metric: {} for metric in metrics},
    }

    for query_data in data:
        # Creating Paths object including both without and with options
        paths = Paths(
            query_data.gold_output_path,
            {
                k: v.predicted_output_path
                for k, v in query_data.predicted_sql_query_without_options.__dict__.items()
            },
            {
                k: v.predicted_output_path
                for k, v in query_data.predicted_sql_query_with_options.__dict__.items()
            },
        )

        # Evaluate predictions without options separately
        for llm, predicted_path in paths.predicted_without_options.items():
            for metric in metrics:
                results["without_options"][metric][f"{llm}"] = results[
                    "without_options"
                ][metric].get(f"{llm}", 0) + evaluate(
                    paths.expected, predicted_path, metric=metric
                )

        # Evaluate predictions with options separately
        for llm, predicted_path in paths.predicted_with_options.items():
            for metric in metrics:
                results["with_options"][metric][f"{llm}"] = results["with_options"][
                    metric
                ].get(f"{llm}", 0) + evaluate(
                    paths.expected, predicted_path, metric=metric
                )

    # After accumulating counts, compute averages for "extra_items" and "missing_items"
    for category in ["with_options", "without_options"]:
        for metric in ["extra_items", "missing_items", "intersection"]:
            for llm, count in results[category][metric].items():
                results[category][metric][llm] = count / len(data)  # Average per query

    return results


if __name__ == "__main__":
    data_paths = {
        # "chants": CHANTS_DATA_PATH,
        "feasts": FEASTS_DATA_PATH,
        # "sources": SOURCES_DATA_PATH,
    }

    all_counts = {name: evaluate_data(path) for name, path in data_paths.items()}

    # Print or output the results in the desired structure
    print(json.dumps(all_counts, indent=4))

import json
from typing import Dict, List
import pandas as pd
from scipy.stats import spearmanr
from query_data import QueryData

CHANTS_DATA_PATH = "data/chants.json"
FEASTS_DATA_PATH = "data/feasts.json"
SOURCES_DATA_PATH = "data/sources.json"


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


def precision_recall(tp, fp, fn):
    """
    Calculate precision and recall.
    """
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = (2 * precision * recall) / (precision + recall)
    return precision, recall, f1


all_metrics = {
    "unordered": lambda expected_ids, actual_ids: expected_ids.sort_values()
    .reset_index(drop=True)
    .equals(actual_ids.sort_values().reset_index(drop=True)),
    "ordered": lambda expected_ids, actual_ids: expected_ids.equals(actual_ids),
    "tp": lambda expected_ids, actual_ids: len(set(expected_ids) & set(actual_ids)),
    "fp": lambda expected_ids, actual_ids: len(set(actual_ids) - set(expected_ids)),
    "fn": lambda expected_ids, actual_ids: len(set(expected_ids) - set(actual_ids)),
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

        # Evaluate predictions without options
        for llm, predicted_path in paths.predicted_without_options.items():
            expected_data = pd.read_csv(paths.expected)
            actual_data = pd.read_csv(predicted_path)

            try:
                expected_ids = expected_data["id"]
                actual_ids = actual_data["id"]
            except KeyError:
                continue

            for metric in metrics:
                score = all_metrics[metric](expected_ids, actual_ids)
                results["without_options"][metric][llm] = (
                    results["without_options"][metric].get(llm, 0) + score
                )

        # Evaluate predictions with options
        for llm, predicted_path in paths.predicted_with_options.items():
            expected_data = pd.read_csv(paths.expected)
            actual_data = pd.read_csv(predicted_path)

            try:
                expected_ids = expected_data["id"]
                actual_ids = actual_data["id"]
            except KeyError:
                continue

            for metric in metrics:
                score = all_metrics[metric](expected_ids, actual_ids)
                results["with_options"][metric][llm] = (
                    results["with_options"][metric].get(llm, 0) + score
                )

    return results


def aggregate_results(
    data_paths: Dict[str, str]
) -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Combine results of multiple datasets into a unified structure.
    """
    combined_results = {
        "with_options": {metric: {} for metric in all_metrics.keys()},
        "without_options": {metric: {} for metric in all_metrics.keys()},
    }

    for name, path in data_paths.items():
        individual_results = evaluate_data(path)

        for category in ["with_options", "without_options"]:
            for metric, llm_scores in individual_results[category].items():
                for llm, score in llm_scores.items():
                    combined_results[category][metric][llm] = (
                        combined_results[category][metric].get(llm, 0) + score
                    )

    # Compute precision and recall
    for category in ["with_options", "without_options"]:
        combined_results[category]["precision"] = {}
        combined_results[category]["recall"] = {}
        combined_results[category]["f1"] = {}
        for llm in combined_results[category]["tp"]:
            tp = combined_results[category]["tp"].get(llm, 0)
            fp = combined_results[category]["fp"].get(llm, 0)
            fn = combined_results[category]["fn"].get(llm, 0)
            precision, recall, f1 = precision_recall(tp, fp, fn)
            combined_results[category]["precision"][llm] = precision
            combined_results[category]["recall"][llm] = recall
            combined_results[category]["f1"][llm] = f1

    return combined_results


if __name__ == "__main__":
    data_paths = {
        "chants": CHANTS_DATA_PATH,
        "feasts": FEASTS_DATA_PATH,
        "sources": SOURCES_DATA_PATH,
    }

    combined_counts = aggregate_results(data_paths)

    # Print or output the combined results
    print(json.dumps(combined_counts, indent=4))

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


def calculate_precision_recall_f1(expected_ids, actual_ids) -> Dict[str, float]:
    expected_set = set(expected_ids)
    actual_set = set(actual_ids)

    true_positives = len(expected_set.intersection(actual_set))
    false_positives = len(actual_set - expected_set)
    false_negatives = len(expected_set - actual_set)

    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 0
    )
    f1_score = (
        2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    )

    out = {"precision": precision, "recall": recall, "f1": f1_score}
    print(out)
    return out


all_metrics = {
    "unordered": lambda expected_ids, actual_ids: expected_ids.sort_values()
    .reset_index(drop=True)
    .equals(actual_ids.sort_values().reset_index(drop=True)),
    "ordered": lambda expected_ids, actual_ids: expected_ids.equals(actual_ids),
    "precision": lambda expected_ids, actual_ids: calculate_precision_recall_f1(
        expected_ids, actual_ids
    )["precision"],
    "recall": lambda expected_ids, actual_ids: calculate_precision_recall_f1(
        expected_ids, actual_ids
    )["recall"],
    "f1": lambda expected_ids, actual_ids: calculate_precision_recall_f1(
        expected_ids, actual_ids
    )["f1"],
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

    for category in ["with_options", "without_options"]:
        for metric in ["precision", "recall", "f1"]:
            for llm, count in results[category][metric].items():
                results[category][metric][llm] = count / len(data)  # Average by the number of queries 

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
                    if llm not in combined_results[category][metric]:
                        combined_results[category][metric][llm] = 0
                    combined_results[category][metric][llm] += score

    # Average by the number of datasets
    num_datasets = len(data_paths)
    for category in ["with_options", "without_options"]:
        for metric in ["precision", "recall", "f1"]:
            for llm in combined_results[category][metric]:
                print(combined_results[category][metric][llm])
                combined_results[category][metric][llm] /= num_datasets

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

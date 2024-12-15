import json
from typing import Dict, List
import pandas as pd
from query_data import QueryData


CHANTS_DATA_PATH = "data/chants.json"
FEASTS_DATA_PATH = "data/feasts.json"
SOURCES_DATA_PATH = "data/sources.json"


def load_data_as_json(json_path: str) -> List[QueryData]:
    with open(json_path, "r") as file:
        data = json.load(file)
    return [QueryData.from_dict(item) for item in data]


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


class MetricsCalculator:
    @staticmethod
    def _calculate_tp_fp_fn(expected_ids, actual_ids):
        expected_set = set(expected_ids)
        actual_set = set(actual_ids)

        true_positives = len(expected_set & actual_set)
        false_positives = len(actual_set - expected_set)
        false_negatives = len(expected_set - actual_set)

        return true_positives, false_positives, false_negatives

    def __init__(self, expected_ids, actual_ids):
        self.expected_ids = expected_ids
        self.actual_ids = actual_ids
        self.tp, self.fp, self.fn = MetricsCalculator._calculate_tp_fp_fn(
            expected_ids, actual_ids
        )

    def precision(self):
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) > 0 else 0

    def recall(self):
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) > 0 else 0

    def f1(self):
        p = self.precision()
        r = self.recall()
        return 2 * p * r / (p + r) if (p + r) > 0 else 0

    def unordered_equals(self):
        return (
            self.expected_ids.sort_values()
            .reset_index(drop=True)
            .equals(self.actual_ids.sort_values().reset_index(drop=True))
        )

    def ordered_equals(self):
        return self.expected_ids.equals(self.actual_ids)

    all_metric_names = ["unordered", "ordered", "precision", "recall", "f1"]

    def get_all_metrics(self):
        return {
            "unordered": self.unordered_equals(),
            "ordered": self.ordered_equals(),
            "precision": self.precision(),
            "recall": self.recall(),
            "f1": self.f1(),
        }


def get_expected_and_actual_ids(
    expected_data_path: str, actual_data_path: str
) -> tuple[pd.Series, pd.Series]:
    expected_data: pd.DataFrame = pd.read_csv(expected_data_path)
    actual_data: pd.DataFrame = pd.read_csv(actual_data_path)

    try:
        expected_ids = expected_data["id"]
    except KeyError:
        expected_ids = expected_data["col1"]

    try:
        actual_ids = actual_data["id"]
    except KeyError:
        actual_ids = pd.Series()

    return expected_ids, actual_ids


def evaluate_data(data_path: str) -> Dict[str, Dict[str, Dict[str, int]]]:
    """
    Evaluate data from a given path and return counts for each metric, organized by
    "with_options" and "without_options".
    """
    data = load_data_as_json(data_path)
    metrics = MetricsCalculator.all_metric_names

    # Structure the result as a dictionary with categories for with_options and without_options
    results = {
        "without_options": {metric: {} for metric in metrics},
        "with_options": {metric: {} for metric in metrics},
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
            expected_ids, actual_ids = get_expected_and_actual_ids(
                paths.expected, predicted_path
            )
            metrics = MetricsCalculator(expected_ids, actual_ids).get_all_metrics()
            for metric, value in metrics.items():
                results["without_options"][metric][llm] = (
                    results["without_options"][metric].get(llm, 0) + value
                )

        # Evaluate predictions with options separately
        for llm, predicted_path in paths.predicted_with_options.items():
            expected_ids, actual_ids = get_expected_and_actual_ids(
                paths.expected, predicted_path
            )
            metrics = MetricsCalculator(expected_ids, actual_ids).get_all_metrics()
            for metric, value in metrics.items():
                results["with_options"][metric][llm] = (
                    results["with_options"][metric].get(llm, 0) + value
                )

    return results


def aggregate_results(
    data_paths: Dict[str, str]
) -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Combine results of multiple datasets into a unified structure.
    """
    combined_results = {
        "without_options": {
            metric: {} for metric in MetricsCalculator.all_metric_names
        },
        "with_options": {metric: {} for metric in MetricsCalculator.all_metric_names},
    }

    for _, path in data_paths.items():
        individual_results = evaluate_data(path)

        for category in ["with_options", "without_options"]:
            for metric, llm_scores in individual_results[category].items():
                for llm, score in llm_scores.items():
                    if llm not in combined_results[category][metric]:
                        combined_results[category][metric][llm] = 0
                    combined_results[category][metric][llm] += score

    # Average by the number of queries
    num_datasets = len(data_paths)
    for category in ["with_options", "without_options"]:
        for metric in ["precision", "recall", "f1"]:
            for llm in combined_results[category][metric]:
                # Divide by 15 since there are 15 queries per dataset
                combined_results[category][metric][llm] = round(
                    combined_results[category][metric][llm] / (num_datasets * 15), 2
                )

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

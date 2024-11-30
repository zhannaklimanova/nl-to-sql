import json
import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Data:
    sql_query: str
    output_path: str
    natural_language_inputs: List[str]

    def __post_init__(self):
        """
        Convert the output path to an absolute path based on the root directory.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_path = os.path.abspath(os.path.join(base_dir, self.output_path))

class DataManager:
    """
    Manages a collection of `Data` instances.
    """
    def __init__(self):
        self.entries: List[Data] = []

    def load_from_json(self, json_file_path: str):
        """
        Loads data from a single JSON file.
        """
        try:
            with open(json_file_path, "r") as file:
                data = json.load(file)
                if not isinstance(data, list) or not data:
                    print(f"Warning: {json_file_path} is empty or not a valid JSON array.")
                    return
                new_entries = [
                    Data(
                        sql_query=entry["sql_query"],
                        output_path=entry["gold_output_path"],
                        natural_language_inputs=entry["natural_language_inputs"]
                    )
                    for entry in data
                ]
                self.entries.extend(new_entries)
                print(f"Loaded {len(new_entries)} entries from {json_file_path}. Total entries so far: {len(self.entries)}")
        except FileNotFoundError:
            print(f"Error: JSON file not found at {json_file_path}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON file {json_file_path}: {e}")
        except KeyError as e:
            print(f"Error: Missing key in JSON file {json_file_path}: {e}")

    def get_entry_by_query(self, sql_query: str) -> Optional[Data]:
        """
        Retrieves a `Data` instance by its SQL query.
        """
        for entry in self.entries:
            if entry.sql_query == sql_query:
                return entry
        print(f"Error: Entry with SQL query '{sql_query}' not found.")
        return None

    def display_entries(self):
        """
        Displays all entries in the dataset.
        """
        for entry in self.entries:
            print({
                "sql_query": entry.sql_query,
                "output_path": entry.output_path,
                "natural_language_inputs": entry.natural_language_inputs,
            })

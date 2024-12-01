from data import DataManager
from gemini import Gemini
import os

def main():
    manager = DataManager()

    json_directory = "data"

    if not os.path.exists(json_directory):
        print(f"Error: Directory '{json_directory}' not found.")
        return

    json_files = [f for f in os.listdir(json_directory) if f.endswith('.json')]

    if not json_files:
        print(f"No JSON files found in directory '{json_directory}'.")
        return

    for json_file in json_files:
        json_file_path = os.path.join(json_directory, json_file)
        manager.load_from_json(json_file_path)

    manager.display_entries()
    print(f"Total entries loaded: {len(manager.entries)}")

if __name__ == "__main__":
    main()

    llm = Gemini()
    print(
        llm.nlq_to_sql("All Chants that have an 'a' but do not contain the phrase 'ad'")
    )

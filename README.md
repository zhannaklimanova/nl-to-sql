# NL-to-SQL Project Instructions
## Table of Contents

1. [Repository Virtual Environment Setup](#repository-virtual-environment-setup)
2. [CantusDB Setup](#cantusdb-setup)
3. [Middleware Setup](#middleware-setup)
4. [Text to SQL Data Collection Process](#text-to-sql-data-collection-process)
   - [Obtaining Ground Truth Data](#obtaining-ground-truth-data)
   - [Obtaining Predicted Data](#obtaining-predicted-data)
5. [Evaluation Gold and Predicted Outputs](#evaluation-gold-and-predicted-outputs)
6. [Links](#links)

## Repository Virtual Environment Setup
1. Ensure python3 is installed by typing the following into a terminal:
   ```bash
      python3
   ```
   Note the python version used for this project:
   Python 3.11.3 (v3.11.3:f3909b8bc8, Apr  4 2023, 20:12:10) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin
2. Create a virtual environment in the project directory:
   ```
      python3 -m venv .venv
   ```
3. Activate the virtual environment:
   ```
      source .venv/bin/activate
   ```
4. Verify the Python executable being used:
   ```
      which python
   ```
5. Upgrade pip to the latest version:
   ```
      python3 -m pip install --upgrade pip
   ```
6. Confirm the pip version:
   ```
      python3 -m pip --version
   ```
7. Install project dependencies from the requirements.txt file:
   ```
      pip3 install -r requirements.txt
   ```
8. Deactivate the virtual environment when done:
   ```
      deactivate
   ```

## CantusDB Setup
1. Clone the [CantusDB repository](https://github.com/DDMAL/CantusDB) and ensure it is up to date by regularly pulling the latest changes.
2. Follow the instructions on the [Deploying CantusDB Locally for Development](https://github.com/DDMAL/CantusDB/wiki/Deploying-CantusDB-locally-for-development#collecting-static-files) page to set up the website for local development.
3. Obtain the `dev_env` file from the `CantusDB Resources` section. This file must be provided by a CantusDB developer.
4. During the *Populating the Database* step, request the `cantus_dump.sql` file from a CantusDB developer and use it to populate the database.
5. Verify that the setup is complete by confirming that the `Chants`, `Sources`, and `Feasts` sections are accessible via `localhost`.

## Middleware Setup

1. Confirm that the *CantusDB Setup* is complete and the website is functional.
2. Place the `middleware.py` file into the `*/CantusDB/django/cantusdb_project/cantusdb/` directory.
3. Navigate to the `Chants`, `Sources`, or `Feasts` page on the CantusDB website, input search criteria, and click *Apply*.
4. The `middleware.py` script will automatically generate and populate the `nlq_sql.json` and `sql_queries.log` files located in `*/CantusDB/django/cantusdb_project/` directory.
5. Each new search performed on the CantusDB website will update the data in `nlq_sql.json` and `sql_queries.log`.
6. Note that not all SQL queries in these files are relevant. Focus on the query that matches the search results displayed on the website.
7. Refer to the *SQL Output Extraction* section for additional instructions.

## Text to SQL Data Collection Process
### Obtaining Ground Truth Data
1. On the localhost version of the website, navigate to the `Chants`, `Sources`, or `Feasts` pages and enter the desired search information. For example:
   - **Segment**: `CANTUS Database`
   - **General search**: `Montreal`
   - **Country**: `Canada`
   - **Century**: `16th century`
   - **Complete Source/Fragment**: `Complete source`

   Observe that only one result is returned for this search.

   ![image](https://github.com/user-attachments/assets/4f5b6173-d12d-467b-9109-cc29961aeccd)

2. Open the `*/CantusDB/django/cantusdb_project/nlq_sql.json` file and locate the query that matches the inputted search criteria. Look for:
   - A query starting with `SELECT DISTINCT`
   - Conditions such as:
     ```
     UPPER(main_app_institution.country::text) LIKE UPPER('%Canada%')
     AND UPPER(main_app_century.name::text) LIKE UPPER('%16th century%')
     AND UPPER(main_app_institution.name::text) LIKE UPPER('%Montreal%')
     ```
   - A query ending with:
     ```
     ORDER BY main_app_institution.siglum ASC, main_app_source.shelfmark ASC LIMIT 1;
     ```

3. Before executing the SQL query on the Docker Postgres container, remove the trailing `LIMIT 1` from the query. This precaution should be taken for all queries to ensure complete results are retrieved.
4. Ensure the database container for the website is running, then run the following Docker command in a terminal to extract information into a file:

   ```bash
   docker exec cantusdb-postgres-1 psql -U cantusdb -d cantusdb \
   -c "\pset format csv" -c "GOLD_SQL_QUERY" | sed '1d' > */Path-to-the-Repository/nl-to-sql/NL2SQL/gold_outputs/object/object_output_filex.csv
   ```

5. When running the Docker command, replace `GOLD_SQL_QUERY` with the SQL query obtained from the search, update the path information appropriately, and ensure that the object is one of `chants`, `sources`, or `feasts`.

6. Ensure that the `object_output_filex.csv` follows the correct naming convention:
   - `object_output_filex` should be `c`, `s`, or `f` for `chants`, `sources`, or `feasts`, respectively.
   - The `x` value represents the index number of the file within that directory.

7. If everything is formatted correctly, the `object_output_filex.csv` file will be generated in the specified directory.

8. Copy and paste the gold SQL query and the gold output path into the appropriate `chants.json`, `sources.json`, or `feasts.json` file. Add them to the `sql_query` and `gold_output_path` fields.

9. Write the natural language query corresponding to the gold SQL query. Ensure that:
   - It starts with: *Given this database schema, generate a SQL query that shows me all the*.
   - It ends with: *Format your response without any formatting or newlines.*
   - Values are enclosed in single quotes (e.g., `'Canada'`).
   - Attribute names are capitalized (e.g., `Country`).

### Obtaining Predicted Data
1. Prompt the chosen LLM with the `natural_language_inputs` and either `database-schema-with-options` or `database-schema-without-options`. Ensure that the input does not exceed the character limit of the selected LLM.

2. If the LLM generates an SQL query with incorrect formatting, clean it up by:
   - Removing newlines.
   - Adding spaces where necessary.
   - Ensuring the query is formatted as a single line.
3. Ensure the database container for the website is running, then execute the following Docker command in a terminal to extract the information into a file:
   ```bash
   docker exec cantusdb-postgres-1 psql -U cantusdb -d cantusdb \
   -c "\pset format csv" -c "PREDICTED_SQL_QUERY" | sed '1d' > */Path-to-the-Repository/nl-to-sql/NL2SQL/predicted_outputs_without_options/object/llm/object_output_filex.csv
   ```
4. In the Docker command:
   - Replace `PREDICTED_SQL_QUERY` with the cleaned-up query generated by the LLM.
   - Ensure the correct directory is chosen based on the schema used: `predicted_outputs_without_options` or `predicted_outputs_with_options`.
   - Update the `llm` directory name to match the specific LLM being used.
   - Rename the file `object_output_filex.csv` to follow the appropriate naming convention, where `object` corresponds to `c` for `chants`, `s` for `sources`, or `f` for `feasts`, and `x` is the index number of the file.
5. If everything is formatted correctly, the `object_output_filex.csv` file will be generated in the specified directory.
6. Copy and paste the predicted SQL query and the predicted output path into the appropriate `chants.json`, `sources.json`, or `feasts.json` file. Add them under the `predicted_sql_query_with_options` or `predicted_sql_query_without_options` fields within the corresponding `llm` field.

## Evaluation Gold and Predicted Outputs
1. Navigate to the project repository in the terminal and ensure that you are in the `nl-to-sql/NL2SQL` directory:
   ```bash
      cd /Path-to-the-Repository/nl-to-sql/NL2SQL
   ```
2. Run the eval.py script using the Python interpreter from the previously set up virtual environment:
   ```bash
      python3 eval.py
   ```
3. The script will output results resembling the following structure:
```json
{
    "without_options": {
        "unordered": {
            "gpt": 23,
            "claude": 23,
            "grok": 16
        },
        "ordered": {
            "gpt": 16,
            "claude": 15,
            "grok": 11
        },
        "precision": {
            "gpt": 0.7,
            "claude": 0.75,
            "grok": 0.56
        },
        "recall": {
            "gpt": 0.69,
            "claude": 0.74,
            "grok": 0.47
        },
        "f1": {
            "gpt": 0.68,
            "claude": 0.7,
            "grok": 0.48
        }
    },
    "with_options": {
        "unordered": {
            "gpt": 32,
            "claude": 28,
            "grok": 23
        },
        "ordered": {
            "gpt": 23,
            "claude": 16,
            "grok": 10
        },
        "precision": {
            "gpt": 0.92,
            "claude": 0.85,
            "grok": 0.69
        },
        "recall": {
            "gpt": 0.88,
            "claude": 0.78,
            "grok": 0.6
        },
        "f1": {
            "gpt": 0.88,
            "claude": 0.78,
            "grok": 0.61
        }
    }
}
```

## Links
- CantusDB: https://github.com/DDMAL/CantusDB
- CantusDB Wiki: https://github.com/DDMAL/CantusDB/wiki/
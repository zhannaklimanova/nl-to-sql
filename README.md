# NL-to-SQL

## Execution

1. Navigate to the project directory:
   ```bash
   cd <directory-structure>/nl-to-sql/NL2SQL
   ```
2. Run the script using the virtual environment:
    ```bash
   <path-to-venv>.venv/bin/python <directory-structure>/NL2SQL/main_pipeline.py
   ```

## Temporary docker command placeholders
### GOLD
docker exec cantusdb-postgres-1 psql -U cantusdb -d cantusdb -c "\pset format csv" -c "SQL_QUERY" | sed '1d' > ~/Developer/NLP/nl-to-sql/NL2SQL/gold_outputs/sources/sx.csv

### PREDICTED
docker exec cantusdb-postgres-1 psql -U cantusdb -d cantusdb -c "\pset format csv" -c "SQL_QUERY" | sed '1d' > ~/Developer/NLP/nl-to-sql/NL2SQL/predicted_outputs/sources/gpt/sx.csv






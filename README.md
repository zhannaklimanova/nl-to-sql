# NL-to-SQL

## Middleware Setup



## Execution

1. Navigate to the project directory:
   ```bash
   cd <directory-structure>/nl-to-sql/NL2SQL
   ```
2. Run the script using the virtual environment:
    ```bash
   <path-to-venv>.venv/bin/python <directory-structure>/NL2SQL/main_pipeline.py
   ```

## Extracting
### GOLD
docker exec cantusdb-postgres-1 psql -U cantusdb -d cantusdb -c "\pset format csv" -c "SQL_QUERY" | sed '1d' > ~/Developer/NLP/nl-to-sql/NL2SQL/gold_outputs/sources/sx.csv

### PREDICTED
docker exec cantusdb-postgres-1 psql -U cantusdb -d cantusdb -c "\pset format csv" -c "SELECT main_app_source.* FROM main_app_source JOIN main_app_institution ON main_app_source.holding_institution_id = main_app_institution.id JOIN main_app_segment ON main_app_source.segment_id = main_app_segment.id WHERE main_app_segment.name = 'CANTUS Database' ORDER BY main_app_institution.siglum, main_app_source.shelfmark;" | sed '1d' > ~/Developer/NLP/nl-to-sql/NL2SQL/predicted_outputs_without_options/sources/gpt/s1.csv






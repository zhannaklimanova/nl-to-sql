# NL-to-SQL

## CantusDB and Middleware Setup
1. Clone the CantusDB repository: https://github.com/DDMAL/CantusDB
2. Follow instructions on the following page to setup local development of the website: https://github.com/DDMAL/CantusDB/wiki/Deploying-CantusDB-locally-for-development#collecting-static-files
3. The ```dev_env``` file content from ```CantusDB Resources``` needs to be obtained from a developer of CantusDB.
4. In the *Populating the database* section of the setup, the ```cantus_dump.sql``` needs to be obtained from a developer of CantusDB.
5. Ensure the setup is complete by verifying that ```Chants```, ```Sources```, and ```Feasts``` sections are all accessible from localhost.
6. Insert the ```middleware.py``` file into ```*/CantusDB/django/cantusdb_project/cantusdb/``` directory.
7. Go on the ```Chants```, ```Sources```, or ```Feasts``` page, input some information for search, and click *Apply*.
8. The ```middleware.py``` file should automatically populate ```nlq_sql.json``` and ```sql_queries.log``` files.
9. The SQL data in ```nlq_sql.json``` and ```sql_queries.log``` will change once a new search on the CantusDB website is issued.
10. Not all the SQL queries in the ```nlq_sql.json``` and ```sql_queries.log``` are useful. Look only for the query that pertains to the returned information on the website.
11. Follow the *SQL Output Extraction* section for more details.


## nl-to-sql Project Setup
1. Navigate to the project directory:
   ```bash
   cd <directory-structure>/nl-to-sql/NL2SQL
   ```
2. Run the script using the virtual environment:
    ```bash
   <path-to-venv>.venv/bin/python <directory-structure>/NL2SQL/main_pipeline.py
   ```

## SQL Output Extraction
### GOLD
docker exec cantusdb-postgres-1 psql -U cantusdb -d cantusdb -c "\pset format csv" -c "SQL_QUERY" | sed '1d' > ~/Developer/NLP/nl-to-sql/NL2SQL/gold_outputs/sources/sx.csv

### PREDICTED
docker exec cantusdb-postgres-1 psql -U cantusdb -d cantusdb -c "\pset format csv" -c "SELECT main_app_source.* FROM main_app_source JOIN main_app_institution ON main_app_source.holding_institution_id = main_app_institution.id JOIN main_app_segment ON main_app_source.segment_id = main_app_segment.id WHERE main_app_segment.name = 'CANTUS Database' ORDER BY main_app_institution.siglum, main_app_source.shelfmark;" | sed '1d' > ~/Developer/NLP/nl-to-sql/NL2SQL/predicted_outputs_without_options/sources/gpt/s1.csv






***Quickstart Guide***

**To test the scripts yourself locally**:
1. Go to https://developer.riotgames.com/
2. Generate an API key
3. Clone the repo and checkout branch 'feature/api-integration'
4. Install dependencies: `pip install -r requirements.txt`
4. **Setup Environment**: 
   - Create a `.env` file based on `.env.example`.
   - Ensure a local MySQL instance is running. (**install MySQL, create the empty schema named lol_prediction_db**)
      - https://dev.mysql.com/downloads/mysql/
      - https://dev.mysql.com/downloads/workbench/

5. **To run API tests**:
   - `python -m api_setup.tests.test_stress`
   - `python -m api_setup.tests.test_security`
   - `python -m api_setup.tests.test_riot_api_connection`

6. **To run database tests**:
   - run `python -m database_setup.db_manager` to build the tables
   - run `python -m database_setup.tests.test_database_integration`

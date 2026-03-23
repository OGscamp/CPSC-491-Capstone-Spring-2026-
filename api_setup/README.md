API script to retrieve a user's PUUID and store data into MySQL database

Demo usage:
1. Copy `.env.example` to `.env` and set `RIOT_API_KEY` and `DB_PASSWORD`.
2. Start local MySQL and run `python -m database_setup.db_manager`.
3. Run `python demo.py --name YourName --tag YourTag --count 5`.
4. For no DB run: `python demo.py --no-db`.

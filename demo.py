import argparse
import sys
from api_setup.api_controller import RiotAPIProvider
from database_setup.db_manager import initialize_db, save_player


def parse_args():
    parser = argparse.ArgumentParser(description="Run demo: fetch Riot PUUID + match IDs + save player to DB")
    parser.add_argument("--name", default="Dedgurs", help="Riot summoner name")
    parser.add_argument("--tag", default="Meow", help="Riot summoner tag line")
    parser.add_argument("--count", type=int, default=5, help="Number of match IDs to fetch")
    parser.add_argument("--no-db", action="store_true", help="Skip DB save and initialization")
    return parser.parse_args()


def main():
    args = parse_args()
    print("\n=== Riot Demo Script ===")
    print(f"Name: {args.name}, Tag: {args.tag}, Count: {args.count}")

    if not args.no_db:
        print("Initializing database tables...")
        initialize_db()

    try:
        provider = RiotAPIProvider()
    except Exception as e:
        print(f"ERROR: Could not initialize RiotAPIProvider: {e}")
        return 1

    puuid = provider.get_puuid(args.name, args.tag)
    if not puuid:
        print("Demo failed: could not retrieve PUUID.")
        return 2

    print(f"Retrieved PUUID: {puuid}")

    match_ids = provider.get_match_ids(puuid, count=args.count)
    print(f"Match IDs ({len(match_ids)}): {match_ids}")

    if not args.no_db:
        print("Saving player to DB...")
        save_player(puuid, args.name)
        print("Saved to DB.")

    print("Demo completed successfully.")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

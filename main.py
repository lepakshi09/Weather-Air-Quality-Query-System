import argparse
from fetch import get_weather, display_pollution_board
from process import init_db, save_weather, get_all_weather, get_latest_weather
from db_menu import menu
from fetch_historicaldata import fetch_historical, backfill
from visualise import visualise

def main():
    parser = argparse.ArgumentParser(description="Unified Weather Monitoring System")
    parser.add_argument("--city", type=str, help="City name")
    parser.add_argument("--menu", action="store_true", help="Open DB menu")
    parser.add_argument("--backfill", type=int, help="Fetch past N days of historical data")
    parser.add_argument("--visualise", action="store_true", help="Plot weather trends")
    args = parser.parse_args()

    init_db()

    if args.menu:
        menu()
        return

    if args.city and args.backfill:
        # Historical backfill mode
        backfill(args.city, args.backfill)
        return

    if args.city:
        # Current data mode (with pollution board)
        result = get_weather(args.city)
        if result:
            display_pollution_board(args.city, result)
            save_weather({
                "city": result["city"],
                "temp": result["temp"],
                "humidity": result["humidity"],
                "description": result["description"],
                "AQI": result.get("AQI"),
                "Components": result.get("Components", {})
            })
            print("✅ Current record saved to database!")

            if args.visualise:
                visualise(city=args.city, days=7)  # default: last 7 days

            latest = get_latest_weather(args.city)
            if latest:
                print(f"Latest record for {args.city}: {latest}")
        else:
            print("❌ Failed to fetch current weather.")

    else:
        print("No city provided. Showing saved records:")
        records = get_all_weather(order="asc")
        for row in records:
            print(row)

if __name__ == "__main__":
    main()
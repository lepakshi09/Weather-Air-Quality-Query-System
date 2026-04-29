import argparse
import time
from fetch import get_weather, display_pollution_board
from process import save_weather, init_db

def run_scheduler(city, interval=3600):
    """Fetch weather + pollution data for a city at fixed intervals."""
    init_db()
    while True:
        result = get_weather(city)
        if result:
            # Show pollution board each time
            display_pollution_board(city, result)

            # Save weather + pollution info into DB
            save_weather({
                "city": result.get("city"),
                "temp": result.get("temp"),
                "humidity": result.get("humidity"),
                "description": result.get("description"),
                "AQI": result.get("AQI"),
                "Components": {
                    "pm10": result.get("Components", {}).get("pm10"),
                    "pm2_5": result.get("Components", {}).get("pm2_5"),
                    "so2": result.get("Components", {}).get("so2"),
                    "no2": result.get("Components", {}).get("no2")
                }
            })

            print(f"✅ Logged at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"❌ Failed to fetch data for {city}")

        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weather + Pollution Scheduler")
    parser.add_argument("--city", type=str, required=True, help="City name to fetch weather")
    parser.add_argument("--interval", type=int, default=3600, help="Interval in seconds (default 1 hour)")
    args = parser.parse_args()

    run_scheduler(city=args.city, interval=args.interval)
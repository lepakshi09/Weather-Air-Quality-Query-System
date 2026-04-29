import argparse
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

DB_NAME = "weather.db"

def fetch_records(city):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT city, temp, humidity, aqi, pm10, pm2_5, so2, no2, timestamp FROM weather WHERE city=?", (city,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def parse_timestamps(records):
    timestamps = []
    for r in records:
        try:
            ts = r[-1]
            # Handle both date-only and full datetime
            if len(ts) == 10:  # format YYYY-MM-DD
                timestamps.append(datetime.strptime(ts, "%Y-%m-%d"))
            else:  # format YYYY-MM-DD HH:MM:SS
                timestamps.append(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"))
        except Exception:
            timestamps.append(None)
    return timestamps

def visualise(city, hours=None, days=None, months=None, year=False, from_date=None, to_date=None):
    records = fetch_records(city)
    if not records:
        print(f"No records found for {city}")
        return

    timestamps = parse_timestamps(records)

    # Apply filters
    cutoff = None
    if hours:
        cutoff = datetime.now() - timedelta(hours=hours)
    elif days:
        cutoff = datetime.now() - timedelta(days=days)
    elif months:
        cutoff = datetime.now() - timedelta(days=30*months)
    elif year:
        cutoff = datetime.now() - timedelta(days=365)

    filtered = []
    for r, t in zip(records, timestamps):
        if not t:
            continue
        if cutoff and t < cutoff:
            continue
        if from_date and t < datetime.strptime(from_date, "%Y-%m-%d"):
            continue
        if to_date and t > datetime.strptime(to_date, "%Y-%m-%d"):
            continue
        filtered.append((r, t))

    if not filtered:
        print("No data in the selected range.")
        return

    # Extract values
    times = [t for (_, t) in filtered]
    temps = [r[1] for (r, _) in filtered]
    humidity = [r[2] for (r, _) in filtered]
    aqi = [r[3] for (r, _) in filtered]
    pm10 = [r[4] for (r, _) in filtered]
    pm25 = [r[5] for (r, _) in filtered]
    so2 = [r[6] for (r, _) in filtered]
    no2 = [r[7] for (r, _) in filtered]

    # Plot
    plt.figure(figsize=(12, 8))

    plt.subplot(2, 1, 1)
    plt.plot(times, temps, label="Temperature (°C)", color="red")
    plt.plot(times, humidity, label="Humidity (%)", color="blue")
    plt.legend()
    plt.title(f"Weather Trends for {city}")
    plt.xticks(rotation=45)

    plt.subplot(2, 1, 2)
    plt.plot(times, aqi, label="AQI", color="green")
    plt.plot(times, pm10, label="PM10", color="orange")
    plt.plot(times, pm25, label="PM2.5", color="purple")
    plt.plot(times, so2, label="SO2", color="brown")
    plt.plot(times, no2, label="NO2", color="black")
    plt.legend()
    plt.title(f"Pollution Trends for {city}")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualise weather and pollution data")
    parser.add_argument("--city", required=True, help="City name")
    parser.add_argument("--hours", type=int, help="Number of hours to filter data")
    parser.add_argument("--days", type=int, help="Number of days to filter data")
    parser.add_argument("--months", type=int, help="Number of months to filter data")
    parser.add_argument("--year", action="store_true", help="Filter data for the last year")
    parser.add_argument("--from", dest="from_date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="to_date", help="End date (YYYY-MM-DD)")
    args = parser.parse_args()

    visualise(args.city, args.hours, args.days, args.months, args.year, args.from_date, args.to_date)
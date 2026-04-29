import sqlite3
from datetime import datetime

DB_NAME = "weather.db"

def init_db():
    """Initialize the SQLite database and ensure schema is up to date."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temp REAL,
            humidity REAL,
            description TEXT,
            timestamp TEXT
        )
    """)

    # Check existing columns
    cursor.execute("PRAGMA table_info(weather)")
    existing_cols = [col[1] for col in cursor.fetchall()]

    # Add missing pollution columns if not present
    required_cols = {
        "aqi": "INTEGER",
        "pm10": "REAL",
        "pm2_5": "REAL",
        "so2": "REAL",
        "no2": "REAL"
    }

    for col, col_type in required_cols.items():
        if col not in existing_cols:
            cursor.execute(f"ALTER TABLE weather ADD COLUMN {col} {col_type}")

    conn.commit()
    conn.close()
def save_weather(data):
    """Save a weather + pollution record into the database with correct timestamp."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Use provided timestamp if available, else fallback to system time
    timestamp = data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO weather (city, temp, humidity, description, aqi, pm10, pm2_5, so2, no2, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("city"),
        data.get("temp"),
        data.get("humidity"),
        data.get("description"),
        data.get("AQI"),
        data.get("Components", {}).get("pm10"),
        data.get("Components", {}).get("pm2_5"),
        data.get("Components", {}).get("so2"),
        data.get("Components", {}).get("no2"),
        timestamp
    ))
    conn.commit()
    conn.close()

def get_all_weather(order="desc"):
    """Retrieve all weather records ordered by timestamp."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT city, temp, humidity, description, aqi, pm10, pm2_5, so2, no2, timestamp
        FROM weather
        ORDER BY timestamp {order.upper()}
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_weather_for_plot(city=None):
    """Retrieve weather records for visualization (optionally filtered by city)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if city:
        cursor.execute("""
            SELECT city, temp, humidity, aqi, pm10, pm2_5, so2, no2, timestamp
            FROM weather
            WHERE city = ?
            ORDER BY timestamp ASC
        """, (city,))
    else:
        cursor.execute("""
            SELECT city, temp, humidity, aqi, pm10, pm2_5, so2, no2, timestamp
            FROM weather
            ORDER BY timestamp ASC
        """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_latest_weather(city):
    """Retrieve the latest weather record for a specific city."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT city, temp, humidity, description, aqi, pm10, pm2_5, so2, no2, timestamp
        FROM weather
        WHERE city = ?
        ORDER BY timestamp DESC
        LIMIT 1
    """, (city,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_all_cities():
    """Retrieve distinct city names from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT city FROM weather ORDER BY city ASC")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

if __name__ == "__main__":
    init_db()
    print("Database initialized with pollution fields!")
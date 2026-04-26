from flask import Flask, request, jsonify, send_file
import sqlite3
import datetime

app = Flask(__name__)
import os

DB_NAME = os.getenv("DB_PATH", "/var/data/sensor_data.db")


# ----------------------
# DB 초기화
# ----------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS barometer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device TEXT,
        server_time TEXT,
        pressure REAL,
        temperature REAL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS gps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gps_time TEXT,
        lat REAL,
        lng REAL
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ----------------------
# 데이터 수신 API
# ----------------------
@app.route('/download-db', methods=['GET'])
def download_db():
    return send_file(
        "/var/data/sensor_data.db",
        as_attachment=True
    )
    
@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    device = data.get("type")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    now = datetime.datetime.now().isoformat()

    # -------- Barometer --------
    if device in ["FixedBarometer", "MovingBarometer"]:
        pressure = data.get("pressure")
        temperature = data.get("temperature")

        c.execute("""
            INSERT INTO barometer (device, server_time, pressure, temperature)
            VALUES (?, ?, ?, ?)
        """, (device, now, pressure, temperature))

        print(f"[{device}] {pressure} Pa | {temperature} C")

    # -------- GPS --------
    elif device == "GPSTracker":
        gps_time = data.get("time")
        lat = data.get("lat")
        lng = data.get("lng")

        c.execute("""
            INSERT INTO gps (gps_time, lat, lng)
            VALUES (?, ?, ?)
        """, (gps_time, lat, lng))

        print(f"[GPS] {gps_time} | ({lat}, {lng})")

    else:
        return jsonify({"status": "error", "msg": "unknown device"})

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


# ----------------------
# 실행
# ----------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

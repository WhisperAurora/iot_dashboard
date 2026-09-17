from flask import Flask, render_template, jsonify
import sqlite3
import random
import datetime
import threading
import time

app = Flask(__name__)
DATABASE = 'sensor_data.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  temperature REAL,
                  humidity REAL,
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

def insert_data(temp, humidity):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('INSERT INTO sensor_data (temperature, humidity, timestamp) VALUES (?, ?, ?)',
              (temp, humidity, now))
    conn.commit()
    conn.close()

def get_recent_data(limit=20):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT temperature, humidity, timestamp FROM sensor_data ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    rows.reverse()
    return rows

def simulate_sensor():
    while True:
        temp = round(random.uniform(20.0, 35.0), 1)
        humidity = round(random.uniform(40.0, 80.0), 1)
        insert_data(temp, humidity)
        time.sleep(5)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    data = get_recent_data(20)
    result = {
        'timestamps': [row[2] for row in data],
        'temperature': [row[0] for row in data],
        'humidity': [row[1] for row in data]
    }
    return jsonify(result)

if __name__ == '__main__':
    init_db()
    thread = threading.Thread(target=simulate_sensor, daemon=True)
    thread.start()
    app.run(debug=True)

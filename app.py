import io
import os
import csv
import sqlite3
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "aceest.db")
PORT = int(os.environ.get("PORT", "5000"))

PROGRAMS = {
    "Fat Loss (FL)": {
        "workout": "Mon: 5x5 Back Squat + AMRAP\nTue: EMOM 20min Assault Bike...",
        "diet": "B: 3 Egg Whites + Oats Idli\nTarget: 2,000 kcal",
        "color": "#e74c3c"
    },
    "Muscle Gain (MG)": {
        "workout": "Mon: Squat 5x5\nTue: Bench 5x5...",
        "diet": "B: 4 Eggs + PB Oats\nTarget: 3,200 kcal",
        "color": "#2ecc71"
    },
    "Beginner (BG)": {
        "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups.",
        "diet": "Balanced Tamil Meals: Idli-Sambar, Rice-Dal...",
        "color": "#3498db"
    }
}


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY, name TEXT, bmi REAL)')
    conn.commit()
    conn.close()


@app.route('/health', methods=['GET'])
def health():
    """Liveness/readiness probe target for Jenkins and Kubernetes."""
    return jsonify({"status": "healthy", "service": "ACEest Fitness"}), 200


@app.route('/programs', methods=['GET'])
def get_all_programs():
    return jsonify(PROGRAMS), 200


@app.route('/calculate', methods=['POST'])
def calculate_bmi():
    data = request.get_json(silent=True)
    if not data or 'weight' not in data or 'height' not in data:
        return jsonify({"error": "Missing data"}), 400

    height_m = data['height'] / 100
    bmi = round(data['weight'] / (height_m ** 2), 2)
    return jsonify({"bmi": bmi, "message": "Stay fit!"}), 200


@app.route('/export/csv', methods=['GET'])
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Program', 'Workout', 'Diet'])
    for name, details in PROGRAMS.items():
        writer.writerow([name, details['workout'], details['diet']])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=fitness_plans.csv"}
    )


@app.route('/client', methods=['POST'])
def save_client():
    init_db()
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clients (name, bmi) VALUES (?, ?)", (data['name'], data['bmi']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Client data persisted to SQLite"}), 201


@app.route('/status', methods=['GET'])
def get_gym_status():
    metrics = {
        "capacity": 150,
        "current_utilization": "85%",
        "status": "Peak Hours",
        "recommendation": "Suggest off-peak training for new joiners"
    }
    return jsonify(metrics), 200


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=PORT)

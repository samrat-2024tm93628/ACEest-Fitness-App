import io
import csv
import sqlite3
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

# Moving your original data store into the Web App logic
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

@app.route('/health', methods=['GET'])
def health():
    """Requirement: Secondary validation layer for Jenkins."""
    return jsonify({"status": "healthy", "service": "ACEest Fitness"}), 200

@app.route('/programs', methods=['GET'])
def get_all_programs():
    """Returns all available fitness programs."""
    return jsonify(PROGRAMS), 200

@app.route('/calculate', methods=['POST'])
def calculate_bmi():
    """Requirement: Modular logic for Pytest validation."""
    data = request.get_json()
    if not data or 'weight' not in data or 'height' not in data:
        return jsonify({"error": "Missing data"}), 400
    
    # BMI Logic
    height_m = data['height'] / 100
    bmi = round(data['weight'] / (height_m ** 2), 2)
    return jsonify({"bmi": bmi, "message": "Stay fit!"}), 200

@app.route('/export/csv', methods=['GET'])
def export_csv():
    """Requirement: Data modularization and export."""
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

def init_db():
    conn = sqlite3.connect('aceest.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY, name TEXT, bmi REAL)')
    conn.commit()
    conn.close()

init_db()

@app.route('/client', methods=['POST'])
def save_client():
    data = request.json
    conn = sqlite3.connect('aceest.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clients (name, bmi) VALUES (?, ?)", (data['name'], data['bmi']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Client data persisted to SQLite"}), 201

@app.route('/status', methods=['GET'])
def get_gym_status():
    """Advanced metrics for gym capacity management."""
    metrics = {
        "capacity": 150,
        "current_utilization": "85%",
        "status": "Peak Hours",
        "recommendation": "Suggest off-peak training for new joiners"
    }
    return jsonify(metrics), 200

if __name__ == '__main__':
    # host='0.0.0.0' is required for Docker to expose the port
    app.run(host='0.0.0.0', port=5000)
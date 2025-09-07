import csv
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)


def load_zodiac_plants(csv_path):
    plants = {}
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sign = row['zodiac_sign'].capitalize()
            plants[sign] = {
                'date_range': row['date_range'],
                'element': row['element'],
                'recommended_plants': [p.strip() for p in row['recommended_plants'].split('|')],
                'why_suitable': row['why_suitable'],
                'source_urls': [url.strip() for url in row['source_urls'].split('|')]
            }
    return plants


# ✅ Load CSV safely from the same folder as app.py
BASE_DIR = os.path.dirname(_file_)  # directory where app.py lives
csv_path = os.path.join(BASE_DIR, "zodiac_plants_real.csv")
zodiac_plants = load_zodiac_plants(csv_path)


def get_zodiac_sign(day, month):
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Sagittarius"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Aquarius"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "Pisces"
    else:
        return None


# Anonymous comments storage (in-memory)
comments = []


@app.route('/')
def home():
    return "Welcome to the Zodiac Plant Recommendation API! Use POST /recommend with 'birthdate' or 'zodiac'."


@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    zodiac_sign = None

    if 'birthdate' in data:
        try:
            birth_date = datetime.strptime(data['birthdate'], "%Y-%m-%d")
            zodiac_sign = get_zodiac_sign(birth_date.day, birth_date.month)
            if not zodiac_sign:
                return jsonify({"error": "Invalid birthdate"}), 400
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400
    elif 'zodiac' in data:
        zodiac_sign = data['zodiac'].capitalize()
        if zodiac_sign not in zodiac_plants:
            return jsonify({"error": "Invalid zodiac sign"}), 400
    else:
        return jsonify({"error": "Missing data"}), 400

    plant_info = zodiac_plants.get(zodiac_sign)
    if plant_info:
        return jsonify({
            "zodiac": zodiac_sign,
            "date_range": plant_info['date_range'],
            "element": plant_info['element'],
            "recommended_plants": plant_info['recommended_plants'],
            "why_suitable": plant_info['why_suitable'],
            "source_urls": plant_info['source_urls']
        })
    else:
        return jsonify({"error": "Zodiac sign not recognized"}), 400


# Endpoint to get all comments
@app.route('/comments', methods=['GET'])
def get_comments():
    return jsonify(comments)


# Endpoint to add a new comment
@app.route('/comments', methods=['POST'])
def add_comment():
    data = request.json
    comment = data.get('comment', '').strip()
    rating = data.get('rating', 0)
    if comment or rating > 0:
        comments.append({'comment': comment, 'rating': rating})
        return jsonify({"success": True}), 201
    return jsonify({"error": "Empty comment and rating"}), 400


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder = os.path.join(os.getcwd(), 'build')
    if path != "" and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    else:
        return send_from_directory(static_folder, 'index.html')


if _name_ == "_main_":
    app.run(debug=True)

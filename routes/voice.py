import os
import requests
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from database.db import db
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

# Blueprint setup
voice_bp = Blueprint("voice", __name__)
foods = db["foods"]

# Nutritionix API credentials
APP_ID = os.getenv("NUTRITIONIX_APP_ID")
API_KEY = os.getenv("NUTRITIONIX_API_KEY")

# Voice Logging Route
@voice_bp.route("/voice-log", methods=["POST"])
def voice_log():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    try:
        data = request.get_json()
        query = data.get("query", "").strip()

        if not query:
            return jsonify({"error": "No voice input provided"}), 400

        headers = {
            "x-app-id": APP_ID,
            "x-app-key": API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "query": query,
            "timezone": "Asia/Kolkata"
        }

        response = requests.post(
            "https://trackapi.nutritionix.com/v2/natural/nutrients",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            print(f"[API ERROR] Nutritionix status code: {response.status_code}, body: {response.text}")
            return jsonify({
                "error": "Nutritionix API failed",
                "status_code": response.status_code,
                "details": response.text
            }), 502

        nutrition_data = response.json()

        if not nutrition_data.get("foods"):
            return jsonify({"error": "No recognizable food item found."}), 400

        now = datetime.now(pytz.timezone("Asia/Kolkata"))
        hour = now.hour
        user_id = str(session["user_id"])

        # Determine meal type
        if 5 <= hour < 11:
            meal_type = "Breakfast"
        elif 11 <= hour < 16:
            meal_type = "Lunch"
        elif 16 <= hour < 21:
            meal_type = "Dinner"
        else:
            meal_type = "Snack"

        logged_foods = []

        for item in nutrition_data["foods"]:
            food_name = item.get("food_name", "Unknown")
            calories = item.get("nf_calories", 0)

            food_entry = {
                "user_id": user_id,
                "food_name": food_name,
                "calories": calories,
                "meal_type": meal_type,
                "timestamp": now
            }

            insert_result = foods.insert_one(food_entry)
            food_entry["_id"] = str(insert_result.inserted_id)

            logged_foods.append({
                "_id": food_entry["_id"],
                "food_name": food_name,
                "calories": calories,
                "meal_type": meal_type
            })

        print(f"[VOICE LOGGED] User: {user_id}, Query: '{query}', Items: {len(logged_foods)}, Time: {now}")

        return jsonify({
            "message": "Food logged successfully!",
            "items_logged": logged_foods
        }), 200

    except Exception as e:
        print(f"[SERVER ERROR] Voice logging failed: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

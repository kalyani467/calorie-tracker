# routes/food.py

from flask import Blueprint, request, session, jsonify, redirect, render_template
from database.db import db
import requests
import os
from datetime import datetime
from bson.objectid import ObjectId
from bson.errors import InvalidId
import pytz
from werkzeug.utils import secure_filename
import uuid

# Blueprint & Collections
food_bp = Blueprint("food", __name__, url_prefix="/food")
foods = db["foods"]
users = db["users"]

# Nutritionix Setup
NUTRITIONIX_API_KEY = os.getenv("NUTRITIONIX_API_KEY")
NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID")

headers = {
    "x-app-id": NUTRITIONIX_APP_ID,
    "x-app-key": NUTRITIONIX_API_KEY,
    "Content-Type": "application/json"
}

# ✅ Voice/Natural Language Logging
@food_bp.route("/log", methods=["POST"])
def log_food():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    query = data.get("query")
    if not query:
        return jsonify({"error": "Query required"}), 400

    res = requests.post("https://trackapi.nutritionix.com/v2/natural/nutrients", headers=headers, json={"query": query})
    if res.status_code != 200:
        return jsonify({"error": "Failed to fetch food data"}), 400

    food_data = res.json()["foods"][0]
    now = datetime.now(pytz.timezone("Asia/Kolkata"))

    log = {
        "user_id": str(session["user_id"]),
        "food_name": food_data["food_name"],
        "calories": food_data.get("nf_calories", 0),
        "protein": food_data.get("nf_protein", 0),
        "carbs": food_data.get("nf_total_carbohydrate", 0),
        "fat": food_data.get("nf_total_fat", 0),
        "meal_type": data.get("meal_type", "Meal"),
        "timestamp": now
    }

    result = foods.insert_one(log)
    log["_id"] = str(result.inserted_id)
    return jsonify({"message": "Food logged successfully", "log": log}), 201

# ✅ Delete food
@food_bp.route("/delete/<string:food_id>", methods=["DELETE"])
def delete_food(food_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        obj_id = ObjectId(food_id)
    except InvalidId:
        return jsonify({"error": "Invalid food ID"}), 400

    result = foods.delete_one({
        "_id": obj_id,
        "user_id": str(session["user_id"])
    })

    if result.deleted_count == 0:
        return jsonify({"error": "Food not found"}), 404

    return jsonify({"message": "Food deleted successfully"}), 200

# ✅ Barcode Scan
@food_bp.route("/barcode", methods=["POST"])
def barcode_search():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    code = data.get("barcode")
    if not code:
        return jsonify({"error": "Barcode is required"}), 400

    res = requests.get(f"https://trackapi.nutritionix.com/v2/search/item?upc={code}", headers=headers)
    if res.status_code != 200:
        return jsonify({"error": "Failed to fetch item"}), 400

    item = res.json().get("foods", [])
    if not item:
        return jsonify({"error": "Item not found"}), 404

    return jsonify({"item": item[0]}), 200

# ✅ Manual Input
@food_bp.route("/manual", methods=["GET", "POST"])
def manual_input():
    if "user_id" not in session:
        return redirect("/auth/login")

    if request.method == "POST":
        query = request.form.get("query")
        meal_type = request.form.get("meal_type", "Meal")

        if not query:
            return "Food input required", 400

        res = requests.post("https://trackapi.nutritionix.com/v2/natural/nutrients", headers=headers, json={"query": query})
        if res.status_code != 200:
            return "Failed to fetch food data", 400

        food_data = res.json()["foods"][0]

        log = {
            "user_id": str(session["user_id"]),
            "food_name": food_data["food_name"],
            "meal_type": meal_type,
            "calories": food_data.get("nf_calories", 0),
            "protein": food_data.get("nf_protein", 0),
            "carbs": food_data.get("nf_total_carbohydrate", 0),
            "fat": food_data.get("nf_total_fat", 0),
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata"))
        }

        foods.insert_one(log)
        return redirect("/dashboard")

    return render_template("manual_input.html")

# ✅ Image Input & Food Detection
@food_bp.route("/image", methods=["GET", "POST"])
def image_input():
    if "user_id" not in session:
        return redirect("/auth/login")

    if request.method == "POST":
        if "food_image" not in request.files:
            return render_template("image_input.html", error="No image uploaded")

        image = request.files["food_image"]
        if image.filename == "":
            return render_template("image_input.html", error="No selected image")

        filename = secure_filename(image.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join("temp_uploads", unique_name)
        os.makedirs("temp_uploads", exist_ok=True)
        image.save(filepath)

        # 🚧 Simulate recognition (later integrate real model)
        recognized_food = "apple"

        # Get nutrition info
        res = requests.post("https://trackapi.nutritionix.com/v2/natural/nutrients", headers=headers, json={"query": recognized_food})
        if res.status_code != 200:
            return render_template("image_input.html", error="Failed to get nutrition info")

        food_data = res.json()["foods"][0]
        log = {
            "user_id": str(session["user_id"]),
            "food_name": food_data["food_name"],
            "meal_type": "Image",
            "calories": food_data.get("nf_calories", 0),
            "protein": food_data.get("nf_protein", 0),
            "carbs": food_data.get("nf_total_carbohydrate", 0),
            "fat": food_data.get("nf_total_fat", 0),
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata"))
        }

        foods.insert_one(log)
        os.remove(filepath)  # ✅ Clean up temp image
        return render_template("image_input.html", message=f"Food logged: {food_data['food_name']} ({food_data['nf_calories']} kcal)")

    return render_template("image_input.html")

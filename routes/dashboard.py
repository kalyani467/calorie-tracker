from flask import Blueprint, session, jsonify, render_template, redirect
from database.db import db
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import pytz

# Blueprint setup
dashboard_bp = Blueprint("dashboard", __name__)
foods = db["foods"]
users = db["users"]

# ✅ API Endpoint: Dashboard JSON Data
@dashboard_bp.route("/api/dashboard")
def get_dashboard_data():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = str(session["user_id"])

    # Set timezone to IST
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    # Fetch user goal or fallback to default
    try:
        user = users.find_one({"_id": ObjectId(user_id)})
        goal = float(user.get("goal_calories", 2000)) if user else 2000
    except Exception as e:
        print("❌ User fetch error:", e)
        goal = 2000

    # Get meals logged today
    try:
        meals_today = list(foods.find({
            "user_id": user_id,  # Stored as string in DB
            "timestamp": {"$gte": start, "$lt": end}
        }))
    except Exception as e:
        print("❌ Meals fetch error:", e)
        meals_today = []

    # Calculate stats
    consumed = sum(m.get("calories", 0) for m in meals_today)
    remaining = max(0, goal - consumed)
    progress = round((consumed / goal) * 100, 1) if goal > 0 else 0

    # Format meals for frontend
    formatted_meals = [
        {
            "_id": str(m["_id"]),
            "food_name": m.get("food_name", "Unnamed"),
            "calories": m.get("calories", 0),
            "timestamp": m.get("timestamp").isoformat() if m.get("timestamp") else "",
            "meal_type": m.get("meal_type", "Meal")
        }
        for m in meals_today
    ]

    return jsonify({
        "goal": goal,
        "consumed": consumed,
        "remaining": remaining,
        "progress": progress,
        "meals": formatted_meals
    })

# ✅ Generate Zomato-Style Notification (after 8PM only)
def get_daily_notification(consumed, goal):
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)
    if now.hour >= 20:  # After 8PM
        if consumed >= goal:
            return f"🎉 Awesome! You hit your goal of {goal} calories today!"
        else:
            return f"🌟 You’ve consumed {consumed} of {goal} cal. Keep going, you’ve got this!"
    return None

# ✅ Render Dashboard Page with notification
@dashboard_bp.route("/dashboard")
def dashboard_page():
    if "user_id" not in session:
        return redirect("/auth/login")

    user_id = str(session["user_id"])
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    try:
        user = users.find_one({"_id": ObjectId(user_id)})
        goal = float(user.get("goal_calories", 2000)) if user else 2000
    except:
        goal = 2000

    try:
        meals_today = list(foods.find({
            "user_id": user_id,
            "timestamp": {"$gte": start, "$lt": end}
        }))
    except:
        meals_today = []

    consumed = sum(m.get("calories", 0) for m in meals_today)
    notification = get_daily_notification(consumed, goal)

    return render_template("dashboard.html", notification=notification)

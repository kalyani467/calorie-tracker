from flask import Blueprint, session, render_template, redirect, request
from database.db import db
from bson.objectid import ObjectId

# ✅ Add url_prefix here
profile_bp = Blueprint("profile", __name__, url_prefix="/profile")
users = db["users"]

# ✅ View Profile Page => /profile/
@profile_bp.route("/", strict_slashes=False)
def profile_page():
    if "user_id" not in session:
        return redirect("/auth/login")

    try:
        user_id = ObjectId(session["user_id"])
    except Exception:
        return redirect("/auth/logout")  # invalid session, force logout

    user = users.find_one({"_id": user_id})
    if not user:
        return redirect("/auth/logout")

    return render_template("profile.html", user=user)

# ✅ Edit Profile Page => /profile/edit
@profile_bp.route("/edit", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect("/auth/login")

    try:
        user_id = ObjectId(session["user_id"])
    except Exception:
        return redirect("/auth/logout")

    if request.method == "POST":
        updated_data = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "age": int(request.form.get("age") or 0),
            "height": float(request.form.get("height") or 0),
            "weight": float(request.form.get("weight") or 0),
            "goal_calories": float(request.form.get("goal_calories") or 2000)
        }

        users.update_one({"_id": user_id}, {"$set": updated_data})
        return redirect("/profile")

    user = users.find_one({"_id": user_id})
    return render_template("edit_profile.html", user=user)

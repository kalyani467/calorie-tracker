from flask import Blueprint, request, session, redirect, jsonify, render_template
from database.db import db
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)
users = db["users"]

# --------------------------
# SIGNUP ROUTES
# --------------------------

@auth_bp.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.form
    print("Signup FORM data:", data)

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # Validate required fields
    if not name or not email or not password:
        return jsonify({"error": "Missing name, email, or password"}), 400

    existing_user = users.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    # Insert new user
    new_user = {
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
        "age": data.get("age", ""),
        "height": data.get("height", ""),
        "weight": data.get("weight", ""),
        "goal_calories": int(data.get("goal_calories", 2000))
    }

    users.insert_one(new_user)
    return redirect("/auth/login")


# --------------------------
# LOGIN ROUTES
# --------------------------

@auth_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.form
    print("Login FORM data:", data)

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = users.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = str(user["_id"])
    return render_template("/dashboard.html")


# --------------------------
# LOGOUT
# --------------------------

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/auth/login")


# --------------------------
# FORGOT PASSWORD
# --------------------------

@auth_bp.route("/forgot-password", methods=["GET"])
def forgot_password_page():
    return render_template("forgot-password.html")

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    email = request.form.get("email")
    if not email:
        return jsonify({"error": "Missing email field"}), 400

    user = users.find_one({"email": email})
    if not user:
        return jsonify({"error": "Email not registered"}), 404

    # Simulate sending email
    print(f"Password reset email would be sent to {email}")
    return jsonify({"message": "Reset instructions sent to email."})

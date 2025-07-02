import os
# import requests
from flask import Blueprint, request, jsonify, session
# from datetime import datetime
from database.db import db
from dotenv import load_dotenv
# import pytz
# import traceback

# Load environment variables
load_dotenv()

# Blueprint setup
image_bp = Blueprint("image", __name__)
foods = db["foods"]

# API credentials (still loaded if needed later)
HF_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
APP_ID = os.getenv("NUTRITIONIX_APP_ID")
API_KEY = os.getenv("NUTRITIONIX_API_KEY")

# HF_MODEL_URL = "https://api-inference.huggingface.co/models/hysts/food-classifier"

# 🚫 Image logging feature is disabled temporarily
@image_bp.route("/image-log", methods=["POST"])
def image_log():
    return jsonify({
        "error": "Image logging feature is currently disabled."
    }), 403

# ✅ You can re-enable the route by uncommenting the full logic below in future

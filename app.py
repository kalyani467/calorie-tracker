from flask import Flask, render_template, session, jsonify, redirect
from flask_cors import CORS
from flask_session import Session
from dotenv import load_dotenv
from datetime import timedelta
import os

# Load environment variables
load_dotenv()

# Flask App Configuration
app = Flask(
    __name__,
    template_folder="../frontend/templates",  # Make sure this path is correct
    static_folder="../frontend/static"
)

# Secret Key & Session Config
app.secret_key = os.getenv("SECRET_KEY", "defaultsecretkey")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

# Enable Flask Session & CORS
Session(app)
CORS(app, supports_credentials=True)

# ✅ Register Blueprints
from routes.auth import auth_bp
from routes.food import food_bp
from routes.dashboard import dashboard_bp
from routes.voice import voice_bp
from routes.profile import profile_bp
from routes.image  import image_bp
from routes.help import help_bp
from routes.home import home_bp
 
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(food_bp, url_prefix="/food")
app.register_blueprint(dashboard_bp)  # /dashboard
app.register_blueprint(voice_bp, url_prefix="/api")
app.register_blueprint(profile_bp, url_prefix="/profile")
app.register_blueprint(image_bp, url_prefix="/api")
app.register_blueprint(help_bp)
app.register_blueprint(home_bp)

# ✅ Root route: redirect based on session
@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/auth/login")
@app.route("/")
def splash():
    return render_template("splash.html")
"""@app.route("/guide")
def guide():
    return render_template("welcome_guide.html")"""
@app.route("/guide/step1")
def guide_step1():
    return render_template("guide_step1.html")

@app.route("/guide/step2")
def guide_step2():
    return render_template("guide_step2.html")

@app.route("/guide/step3")
def guide_step3():
    return render_template("guide_step3.html")


# ✅ Page to upload image (renders image.html)
@app.route("/upload-image")
def upload_image_page():
    if "user_id" not in session:
        return redirect("/auth/login")
    return render_template("image.html")

# ✅ Check session state
@app.route("/session-check")
def session_check():
    return jsonify({"logged_in": "user_id" in session})

# ✅ 404 Error Handler
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found"}), 404

# ✅ Run App
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

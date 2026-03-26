from flask import Flask, render_template, request, jsonify, redirect, url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import joblib
import pandas as pd
from datetime import datetime
import os, secrets

app = Flask(__name__)

app.config["SECRET_KEY"] = "supersecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

login_manager.login_view = "login"

# Load ML model
model = joblib.load("risk_model.pkl")


# ==============================
# DATABASE MODELS
# ==============================

class User(db.Model, UserMixin):
    id            = db.Column(db.Integer,     primary_key=True)
    username      = db.Column(db.String(150), unique=True, nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=True)
    password      = db.Column(db.String(150), nullable=False)
    is_admin      = db.Column(db.Boolean,     default=False)

    # Settings columns
    first_name    = db.Column(db.String(80),  nullable=True)
    last_name     = db.Column(db.String(80),  nullable=True)
    role          = db.Column(db.String(100), nullable=True)
    organisation  = db.Column(db.String(120), nullable=True)
    bio           = db.Column(db.Text,        nullable=True)
    avatar        = db.Column(db.String(255), nullable=True)
    dark_mode     = db.Column(db.Boolean,     default=False)
    accent_colour = db.Column(db.String(50),  nullable=True)
    font_size     = db.Column(db.String(30),  nullable=True)
    notifications = db.Column(db.JSON,        nullable=True)

    projects      = db.relationship("Project", backref="owner", lazy=True)


class Project(db.Model):
    id        = db.Column(db.Integer,    primary_key=True)
    name      = db.Column(db.String(200))
    risk      = db.Column(db.Float)
    status    = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime,  default=datetime.utcnow)
    user_id   = db.Column(db.Integer,   db.ForeignKey("user.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==============================
# AUTH ROUTES
# ==============================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Username already exists")

        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, password=hashed)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials"

    return render_template("login.html", error=error)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ==============================
# PAGE ROUTES
# ==============================

@app.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/projects")
@login_required
def projects_page():
    return render_template("projects.html")

@app.route("/analytics")
@login_required
def analytics():
    return render_template("analytics.html")

@app.route("/reports")
@login_required
def reports():
    return render_template("reports.html")

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")

@app.route("/billing")
@login_required
def billing():
    return render_template("billing.html")


# ==============================
# ML PREDICTION
# ==============================

@app.route("/predict", methods=["POST"])
@login_required
def predict():
    data = request.json

    progress       = data["progress"]
    deadline       = data["deadline"]
    budget_percent = data["budget"]
    team_size      = data["team"]

    total_tasks       = 100
    completed_tasks   = progress
    avg_task_delay    = deadline / 10
    budget_allocated  = 200000
    budget_spent      = (budget_percent / 100) * budget_allocated
    team_experience   = 5
    sprint_velocity   = 50
    past_delay_rate   = 0.3
    completion_rate   = completed_tasks / total_tasks
    budget_burn_rate  = budget_spent / budget_allocated
    productivity_score = sprint_velocity / team_size

    input_data = pd.DataFrame({
        "total_tasks":        [total_tasks],
        "completed_tasks":    [completed_tasks],
        "avg_task_delay":     [avg_task_delay],
        "budget_allocated":   [budget_allocated],
        "budget_spent":       [budget_spent],
        "team_size":          [team_size],
        "team_experience":    [team_experience],
        "sprint_velocity":    [sprint_velocity],
        "past_delay_rate":    [past_delay_rate],
        "completion_rate":    [completion_rate],
        "budget_burn_rate":   [budget_burn_rate],
        "productivity_score": [productivity_score]
    })

    prediction  = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]
    risk_score  = round(probability * 100, 2)
    status      = "Delayed" if prediction == 1 else "On Track"

    new_project = Project(
        name=data["name"],
        risk=risk_score,
        status=status,
        owner=current_user
    )
    db.session.add(new_project)
    db.session.commit()

    return jsonify({"risk": risk_score, "status": status})


# ==============================
# PROJECT HISTORY
# ==============================

@app.route("/history")
@login_required
def history():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    data = [
        {
            "name":      p.name,
            "risk":      p.risk,
            "status":    p.status,
            "timestamp": p.timestamp.strftime("%Y-%m-%d %H:%M")
        }
        for p in projects
    ]
    return jsonify(data)


# ==============================
# SETTINGS API
# ==============================

@app.route("/api/settings/load")
@login_required
def settings_load():
    return jsonify({
        "first_name":    current_user.first_name    or "",
        "last_name":     current_user.last_name     or "",
        "email":         current_user.email         or "",
        "role":          current_user.role          or "",
        "organisation":  current_user.organisation  or "",
        "bio":           current_user.bio           or "",
        "avatar":        current_user.avatar        or "",
        "dark_mode":     current_user.dark_mode     or False,
        "accent_colour": current_user.accent_colour or "Aurora",
        "font_size":     current_user.font_size     or "Default (15px)",
        "notifications": current_user.notifications or {},
    })


@app.route("/api/settings/profile", methods=["POST"])
@login_required
def settings_profile():
    data = request.get_json()
    try:
        current_user.first_name   = data.get("first_name",   "")
        current_user.last_name    = data.get("last_name",    "")
        current_user.email        = data.get("email",        current_user.email)
        current_user.role         = data.get("role",         "")
        current_user.organisation = data.get("organisation", "")
        current_user.bio          = data.get("bio",          "")
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/settings/password", methods=["POST"])
@login_required
def settings_password():
    data = request.get_json()
    # FIX: use bcrypt (not werkzeug) since that's what you use to hash passwords
    if not bcrypt.check_password_hash(current_user.password, data["current_password"]):
        return jsonify({"success": False, "error": "Current password is incorrect"})
    try:
        current_user.password = bcrypt.generate_password_hash(
            data["new_password"]
        ).decode("utf-8")
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/settings/notifications", methods=["POST"])
@login_required
def settings_notifications():
    data = request.get_json()
    try:
        current_user.notifications = data
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/settings/appearance", methods=["POST"])
@login_required
def settings_appearance():
    data = request.get_json()
    try:
        current_user.dark_mode     = data.get("dark_mode",     False)
        current_user.accent_colour = data.get("accent_colour", "Aurora")
        current_user.font_size     = data.get("font_size",     "Default (15px)")
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/settings/avatar", methods=["POST"])
@login_required
def settings_avatar():
    file = request.files.get("avatar")
    if not file:
        return jsonify({"success": False, "error": "No file received"})

    allowed = {"jpg", "jpeg", "png", "gif", "webp"}
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed:
        return jsonify({"success": False, "error": "File type not allowed"})

    filename = f"avatar_{current_user.id}.{ext}"
    folder   = os.path.join(current_app.static_folder, "avatars")
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, filename))

    current_user.avatar = f"/static/avatars/{filename}"
    db.session.commit()
    return jsonify({"success": True, "url": current_user.avatar})


@app.route("/api/settings/apikeys/generate", methods=["POST"])
@login_required
def generate_api_key():
    new_key = "rp_live_" + secrets.token_hex(24)
    key_id  = secrets.token_hex(8)
    # TODO: persist to an ApiKey table if you need keys to survive restarts
    return jsonify({"success": True, "key": new_key, "key_id": key_id})


@app.route("/api/settings/apikeys/revoke", methods=["POST"])
@login_required
def revoke_api_key():
    # TODO: delete from ApiKey table by key_id
    return jsonify({"success": True})


@app.route("/api/settings/sessions/revoke", methods=["POST"])
@login_required
def revoke_session():
    # TODO: delete session from sessions table by session_id
    return jsonify({"success": True})


@app.route("/api/settings/sessions/revoke-all", methods=["POST"])
@login_required
def revoke_all_sessions():
    # TODO: delete all sessions for current_user except current
    return jsonify({"success": True})


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
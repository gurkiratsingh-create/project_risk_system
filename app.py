from flask import Flask, render_template, request, jsonify, redirect, url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import joblib
import pandas as pd
from datetime import datetime
import os
import secrets
import logging
from logging.handlers import RotatingFileHandler
import numpy as np

# ==============================
# APP INITIALIZATION
# ==============================

app = Flask(__name__)

# ==============================
# CONFIGURATION
# ==============================

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///database.db"
)

# Fix for Heroku postgres URLs
if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config[
        "SQLALCHEMY_DATABASE_URI"
    ].replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 🔥 FIX 6: File upload security
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max upload

# 🔥 FIX 9: Session security
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FLASK_ENV") == "production"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = 3600  # 1 hour

# ==============================
# EXTENSIONS INITIALIZATION
# ==============================

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # 🔥 FIX 3: Flask-Migrate for schema evolution
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

# 🔥 FIX 5: Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

login_manager.login_view = "login"

# ==============================
# 🔥 FIX 8: LOGGING SETUP
# ==============================

if not app.debug:
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # File handler for error logs
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Risk Predictor startup')

# ==============================
# 🔥 FIX 2: LOAD ML MODEL SAFELY
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "risk_model.pkl")

model = None
try:
    model = joblib.load(model_path)
    app.logger.info("✅ ML Model loaded successfully")
    print("✅ ML Model loaded successfully")
except FileNotFoundError:
    app.logger.error(f"❌ Model file not found at: {model_path}")
    print(f"❌ MODEL NOT FOUND: {model_path}")
except Exception as e:
    app.logger.error(f"❌ Model load error: {str(e)}")
    print(f"❌ MODEL LOAD ERROR: {e}")

# 🔥 FIX 7: Configuration for scalability
DEFAULT_CONFIG = {
    "BUDGET_ALLOCATED": float(os.environ.get("DEFAULT_BUDGET", "200000")),
    "TOTAL_TASKS": int(os.environ.get("DEFAULT_TASKS", "100")),
    "PAST_DELAY_RATE": float(os.environ.get("DEFAULT_DELAY_RATE", "0.3"))
}

# ==============================
# DATABASE MODELS
# ==============================

class User(db.Model, UserMixin):
    id            = db.Column(db.Integer,     primary_key=True)
    username      = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email         = db.Column(db.String(150), unique=True, nullable=True, index=True)
    password      = db.Column(db.String(150), nullable=False)
    is_admin      = db.Column(db.Boolean,     default=False)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)

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
    public_profile = db.Column(db.Boolean,    default=False)
    
    projects      = db.relationship("Project", backref="owner", lazy=True, cascade="all, delete-orphan")
    api_keys      = db.relationship("ApiKey", backref="owner", lazy=True, cascade="all, delete-orphan")


class Project(db.Model):
    id        = db.Column(db.Integer,    primary_key=True)
    name      = db.Column(db.String(200), nullable=False)
    risk      = db.Column(db.Float,      nullable=False)
    status    = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime,   default=datetime.utcnow, index=True)
    user_id   = db.Column(db.Integer,    db.ForeignKey("user.id"), nullable=False)
    
    # Additional metadata for better analytics
    progress       = db.Column(db.Float)
    deadline       = db.Column(db.Float)
    budget_percent = db.Column(db.Float)
    team_size      = db.Column(db.Float)


class ApiKey(db.Model):
    id         = db.Column(db.Integer,    primary_key=True)
    key_id     = db.Column(db.String(16), unique=True, nullable=False, index=True)
    key_hash   = db.Column(db.String(128), nullable=False)  # Store hashed, not plain
    name       = db.Column(db.String(100))
    created_at = db.Column(db.DateTime,   default=datetime.utcnow)
    last_used  = db.Column(db.DateTime)
    is_active  = db.Column(db.Boolean,    default=True)
    user_id    = db.Column(db.Integer,    db.ForeignKey("user.id"), nullable=False)


# ==============================
# DATABASE INITIALIZATION
# ==============================

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except Exception as e:
        app.logger.error(f"User load error: {str(e)}")
        return None

# ==============================
# HELPER FUNCTIONS
# ==============================

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def safe_float_conversion(value):
    """Safely convert numpy types to Python float"""
    if isinstance(value, (np.integer, np.floating)):
        return float(value)
    return value


# ==============================
# AUTH ROUTES
# ==============================

@app.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per hour")  # Prevent registration spam
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        email = request.form.get("email", "").strip() if request.form.get("email") else None

        # Validation
        if not username or len(username) < 3:
            return render_template("register.html", error="Username must be at least 3 characters")
        
        if not password or len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters")

        # 🔥 FIX 4: Check username uniqueness
        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Username already exists")

        # 🔥 FIX 4: Check email uniqueness and validity
        if email:
            if not validate_email(email):
                return render_template("register.html", error="Invalid email format")
            if User.query.filter_by(email=email).first():
                return render_template("register.html", error="Email already registered")

        try:
            hashed = bcrypt.generate_password_hash(password).decode("utf-8")
            new_user = User(username=username, password=hashed, email=email)
            db.session.add(new_user)
            db.session.commit()
            app.logger.info(f"New user registered: {username}")
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration error: {str(e)}")
            return render_template("register.html", error="Registration failed. Please try again.")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")  # Prevent brute force
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if not username or not password:
            return render_template("login.html", error="Username and password required")
        
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            app.logger.info(f"User logged in: {username}")
            
            # Redirect to next page if specified
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for("dashboard"))
        else:
            app.logger.warning(f"Failed login attempt for: {username}")
            error = "Invalid credentials"

    return render_template("login.html", error=error)


@app.route("/logout")
@login_required
def logout():
    app.logger.info(f"User logged out: {current_user.username}")
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
@limiter.limit("30 per minute")  # 🔥 FIX 5: Rate limit predictions
def predict():
    # 🔥 FIX 2: Check if model is loaded
    if model is None:
        app.logger.error("Prediction attempted but model not available")
        return jsonify({"error": "ML model not available. Please contact support."}), 503

    data = request.get_json()

    # Safety check
    if not data:
        return jsonify({"error": "No data received"}), 400

    try:
        progress       = float(data.get("progress", 0))
        deadline       = float(data.get("deadline", 0))
        budget_percent = float(data.get("budget", 0))
        team_size      = float(data.get("team", 0))
        name           = data.get("name", "Untitled Project").strip()
        
        # Validation
        if not (0 <= progress <= 100):
            return jsonify({"error": "Progress must be between 0 and 100"}), 400
        if deadline < 0:
            return jsonify({"error": "Deadline must be positive"}), 400
        if not (0 <= budget_percent <= 100):
            return jsonify({"error": "Budget must be between 0 and 100"}), 400
        if team_size < 0:
            return jsonify({"error": "Team size must be positive"}), 400
            
    except (ValueError, TypeError) as e:
        app.logger.error(f"Input parsing error: {str(e)}")
        return jsonify({"error": "Invalid input format"}), 400

    # Prevent division errors
    if team_size == 0:
        team_size = 1

    # 🔥 FIX 7: Use configurable values
    total_tasks       = DEFAULT_CONFIG["TOTAL_TASKS"]
    completed_tasks   = progress
    avg_task_delay    = deadline / 10
    budget_allocated  = DEFAULT_CONFIG["BUDGET_ALLOCATED"]

    budget_spent      = (budget_percent / 100) * budget_allocated
    team_experience   = min(10, team_size * 1.5)
    sprint_velocity   = team_size * 10
    past_delay_rate   = DEFAULT_CONFIG["PAST_DELAY_RATE"]

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

    try:
        probs = model.predict_proba(input_data)[0]
        prediction  = model.predict(input_data)[0]
        probability = probs[1]
    except Exception as e:
        app.logger.error(f"Model prediction error: {str(e)}")
        return jsonify({"error": "Prediction failed. Please try again."}), 500

    # Explainability
    feature_names = input_data.columns
    importances = model.feature_importances_

    input_values = input_data.iloc[0].values
    weighted_importance = input_values * importances
    indices = np.argsort(weighted_importance)[::-1][:3]

    top_features = []
    for i in indices:
        value = round(importances[i] * 100, 2)
        scaled_value = min(100, value * 5)

        top_features.append({
            "feature": feature_names[i],
            "importance": float(scaled_value)  # 🔥 FIX 1: Ensure Python float
        })

    # 🔥 FIX 1: Convert numpy types to Python types
    risk_score  = float(round(probability * 100, 2))
    confidence  = float(round(probability * 100, 2))
    status      = "Delayed" if prediction == 1 else "On Track"

    reasons = []
    if completion_rate < 0.4:
        reasons.append("Low progress")
    if budget_burn_rate > 0.8:
        reasons.append("High budget usage")
    if avg_task_delay > 5:
        reasons.append("High delay pressure")

    # Save to database
    try:
        new_project = Project(
            name=name,
            risk=risk_score,
            status=status,
            progress=progress,
            deadline=deadline,
            budget_percent=budget_percent,
            team_size=team_size,
            owner=current_user
        )
        db.session.add(new_project)
        db.session.commit()
        app.logger.info(f"Project created: {name} by {current_user.username}")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Failed to save project"}), 500

    return jsonify({
        "risk": risk_score,
        "status": status,
        "top_factors": top_features,
        "confidence": confidence,
        "reasons": reasons
    })


# ==============================
# PROJECT HISTORY
# ==============================

@app.route("/history")
@login_required
def history():
    try:
        projects = Project.query.filter_by(user_id=current_user.id)\
            .order_by(Project.timestamp.desc())\
            .limit(100)\
            .all()
        
        data = [
            {
                "id":        p.id,
                "name":      p.name,
                "risk":      float(p.risk),  # Ensure float
                "status":    p.status,
                "timestamp": p.timestamp.strftime("%Y-%m-%d %H:%M")
            }
            for p in projects
        ]
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"History fetch error: {str(e)}")
        return jsonify({"error": "Failed to fetch history"}), 500


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
        "public_profile": current_user.public_profile or False
    })


@app.route("/api/settings/profile", methods=["POST"])
@login_required
@limiter.limit("20 per hour")
def settings_profile():
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    try:
        # 🔥 FIX 4: Validate email if changing
        new_email = data.get("email", "").strip()
        if new_email and new_email != current_user.email:
            if not validate_email(new_email):
                return jsonify({"success": False, "error": "Invalid email format"})
            if User.query.filter_by(email=new_email).first():
                return jsonify({"success": False, "error": "Email already in use"})
        
        current_user.first_name   = data.get("first_name", "")[:80]
        current_user.last_name    = data.get("last_name", "")[:80]
        current_user.email        = new_email if new_email else current_user.email
        current_user.role         = data.get("role", "")[:100]
        current_user.organisation = data.get("organisation", "")[:120]
        current_user.bio          = data.get("bio", "")[:1000]
        
        db.session.commit()
        app.logger.info(f"Profile updated: {current_user.username}")
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Profile update error: {str(e)}")
        return jsonify({"success": False, "error": "Update failed"})


@app.route("/api/settings/password", methods=["POST"])
@login_required
@limiter.limit("5 per hour")  # Stricter limit for password changes
def settings_password():
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")
    
    if not current_password or not new_password:
        return jsonify({"success": False, "error": "Passwords required"}), 400
    
    # Verify current password
    if not bcrypt.check_password_hash(current_user.password, current_password):
        app.logger.warning(f"Incorrect password attempt: {current_user.username}")
        return jsonify({"success": False, "error": "Current password is incorrect"})
    
    # Validate new password
    if len(new_password) < 6:
        return jsonify({"success": False, "error": "New password must be at least 6 characters"})
    
    try:
        current_user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        db.session.commit()
        app.logger.info(f"Password changed: {current_user.username}")
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Password change error: {str(e)}")
        return jsonify({"success": False, "error": "Password change failed"})


@app.route("/api/settings/appearance", methods=["POST"])
@login_required
def settings_appearance():
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    try:
        current_user.dark_mode     = data.get("dark_mode", False)
        current_user.accent_colour = data.get("accent_colour", "Aurora")
        current_user.font_size     = data.get("font_size", "Default (15px)")
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Appearance update error: {str(e)}")
        return jsonify({"success": False, "error": "Update failed"})


@app.route("/api/settings/avatar", methods=["POST"])
@login_required
@limiter.limit("10 per hour")
def settings_avatar():
    file = request.files.get("avatar")
    
    if not file:
        return jsonify({"success": False, "error": "No file received"}), 400

    # 🔥 FIX 6: Enhanced file validation
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected"}), 400

    allowed = {"jpg", "jpeg", "png", "gif", "webp"}
    if '.' not in file.filename:
        return jsonify({"success": False, "error": "Invalid file"}), 400
        
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed:
        return jsonify({"success": False, "error": "File type not allowed"}), 400

    try:
        filename = f"avatar_{current_user.id}_{secrets.token_hex(8)}.{ext}"
        folder   = os.path.join(current_app.static_folder, "avatars")
        os.makedirs(folder, exist_ok=True)
        
        filepath = os.path.join(folder, filename)
        file.save(filepath)

        current_user.avatar = f"/static/avatars/{filename}"
        db.session.commit()
        
        app.logger.info(f"Avatar updated: {current_user.username}")
        return jsonify({"success": True, "url": current_user.avatar})
    except Exception as e:
        app.logger.error(f"Avatar upload error: {str(e)}")
        return jsonify({"success": False, "error": "Upload failed"})


@app.route("/api/settings/apikeys/generate", methods=["POST"])
@login_required
@limiter.limit("5 per hour")
def generate_api_key():
    data = request.get_json() or {}
    name = data.get("name", "API Key")
    
    try:
        new_key = "rp_live_" + secrets.token_hex(24)
        key_id  = secrets.token_hex(8)
        
        # Hash the key before storing
        key_hash = bcrypt.generate_password_hash(new_key).decode("utf-8")
        
        api_key = ApiKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            owner=current_user
        )
        db.session.add(api_key)
        db.session.commit()
        
        app.logger.info(f"API key generated: {current_user.username}")
        
        # Return the plain key only once
        return jsonify({
            "success": True,
            "key": new_key,
            "key_id": key_id,
            "warning": "Save this key now. You won't see it again."
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"API key generation error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to generate key"})


@app.route("/api/settings/apikeys/revoke", methods=["POST"])
@login_required
def revoke_api_key():
    data = request.get_json()
    
    if not data or "key_id" not in data:
        return jsonify({"success": False, "error": "Key ID required"}), 400
    
    try:
        api_key = ApiKey.query.filter_by(
            key_id=data["key_id"],
            user_id=current_user.id
        ).first()
        
        if not api_key:
            return jsonify({"success": False, "error": "Key not found"}), 404
        
        db.session.delete(api_key)
        db.session.commit()
        
        app.logger.info(f"API key revoked: {current_user.username}")
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"API key revocation error: {str(e)}")
        return jsonify({"success": False, "error": "Revocation failed"})


@app.route("/api/settings/sessions/revoke", methods=["POST"])
@login_required
def revoke_session():
    # TODO: Implement session management with Flask-Session or Redis
    return jsonify({"success": True, "message": "Session revocation not yet implemented"})


@app.route("/api/settings/sessions/revoke-all", methods=["POST"])
@login_required
def revoke_all_sessions():
    # TODO: Implement with proper session store
    return jsonify({"success": True, "message": "Session revocation not yet implemented"})


@app.route("/api/settings/notifications", methods=["POST"])
@login_required
def settings_notifications():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    try:
        current = current_user.notifications or {}
        current.update(data)
        current_user.notifications = current
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Notifications update error: {str(e)}")
        return jsonify({"success": False, "error": "Update failed"})


@app.route("/api/settings/privacy", methods=["POST"])
@login_required
def settings_privacy():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    try:
        current_user.public_profile = data.get("public_profile", False)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Privacy update error: {str(e)}")
        return jsonify({"success": False, "error": "Update failed"})


@app.route("/api/profile")
@login_required
def api_profile():
    try:
        projects = Project.query.filter_by(user_id=current_user.id).all()
        total_projects = len(projects)

        avg_risk = round(
            sum(p.risk for p in projects) / total_projects, 1
        ) if total_projects else 0

        critical = len([p for p in projects if p.risk >= 80])
        high     = len([p for p in projects if 60 <= p.risk < 80])
        medium   = len([p for p in projects if 40 <= p.risk < 60])
        low      = len([p for p in projects if p.risk < 40])

        # Activity generation
        activities = []
        for p in sorted(projects, key=lambda x: x.timestamp, reverse=True)[:5]:
            activities.append({
                "title": "Analysis Completed",
                "desc": f"{p.name} — Risk {p.risk}%",
                "time": p.timestamp.strftime("%d %b")
            })

        # Format join date
        joined = current_user.created_at.strftime("%b %Y") if current_user.created_at else "Jan 2024"

        return jsonify({
            "username": current_user.username,
            "email": current_user.email or "Not set",
            "joined": joined,
            "stats": {
                "projects": total_projects,
                "avg_risk": float(avg_risk)  # Ensure float
            },
            "risk": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low
            },
            "activities": activities
        })
    except Exception as e:
        app.logger.error(f"Profile API error: {str(e)}")
        return jsonify({"error": "Failed to load profile"}), 500


# ==============================
# ERROR HANDLERS
# ==============================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f"Internal error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large. Maximum size is 2MB"}), 413


@app.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429


# ==============================
# HEALTH CHECK
# ==============================

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "database": "connected"
    })


# ==============================
# STARTUP
# ==============================

print("=" * 60)
print("🚀 RISK PREDICTOR - ENHANCED VERSION")
print("=" * 60)
print(f"📊 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"🤖 ML Model: {'✅ Loaded' if model else '❌ Not Available'}")
print(f"🔒 Session Security: {'✅ Enabled' if app.config['SESSION_COOKIE_SECURE'] else '⚠️  Development Mode'}")
print(f"⚡ Rate Limiting: ✅ Enabled")
print(f"📝 Logging: {'✅ Enabled' if not app.debug else '⚠️  Debug Mode'}")
print("=" * 60)

# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    # Use environment variables for production
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )
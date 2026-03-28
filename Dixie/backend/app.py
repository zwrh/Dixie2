import datetime
import hashlib
import os
import sqlite3
from functools import wraps

import jwt
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_EXPIRATION_HOURS = 24
CORS(app)

DATABASE = os.path.join(os.path.dirname(__file__), "dixie.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT UNIQUE NOT NULL,
            system_type TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            target_port INTEGER NOT NULL,
            date_added TEXT NOT NULL DEFAULT (datetime('now')),
            last_seen TEXT,
            status TEXT NOT NULL DEFAULT 'responsive'
        )
    """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """
    )
    db.commit()

    # Seed default settings if not exists
    defaults = {
        "ping_interval": "30",
    }
    for key, value in defaults.items():
        db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )
    db.commit()

    # Seed default admin user if not exists (password: admin123)
    existing = db.execute(
        "SELECT id FROM users WHERE username = ?", ("admin",)
    ).fetchone()
    if not existing:
        salt = os.urandom(32).hex()
        password_hash = hashlib.sha256((salt + "admin123").encode()).hexdigest()
        db.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            ("admin", password_hash, salt),
        )
        db.commit()


def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode()).hexdigest()


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        if not token:
            return jsonify({"error": "Token required"}), 401
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            g.user_id = payload["user_id"]
            g.username = payload["username"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()

    if not user or hash_password(password, user["salt"]) != user["password_hash"]:
        return jsonify({"error": "Invalid username or password"}), 401

    token = jwt.encode(
        {
            "user_id": user["id"],
            "username": user["username"],
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
        },
        JWT_SECRET,
        algorithm="HS256",
    )

    return jsonify({"username": user["username"], "token": token})


@app.route("/api/me", methods=["GET"])
@auth_required
def me():
    return jsonify({"username": g.username})


@app.route("/api/change-password", methods=["POST"])
@auth_required
def change_password():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"error": "Both current and new password are required"}), 400

    if len(new_password) < 8:
        return jsonify({"error": "New password must be at least 8 characters"}), 400

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id = ?", (g.user_id,)
    ).fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if hash_password(current_password, user["salt"]) != user["password_hash"]:
        return jsonify({"error": "Current password is incorrect"}), 401

    new_salt = os.urandom(32).hex()
    new_hash = hash_password(new_password, new_salt)
    db.execute(
        "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
        (new_hash, new_salt, g.user_id),
    )
    db.commit()

    return jsonify({"message": "Password updated successfully"})


@app.route("/api/clients", methods=["GET"])
@auth_required
def get_clients():
    db = get_db()
    clients = db.execute("SELECT * FROM clients ORDER BY date_added DESC").fetchall()
    return jsonify([dict(row) for row in clients])


@app.route("/api/stats", methods=["GET"])
@auth_required
def get_stats():
    db = get_db()
    total_clients = db.execute("SELECT COUNT(*) as count FROM clients").fetchone()[
        "count"
    ]
    online_clients = db.execute(
        "SELECT COUNT(*) as count FROM clients WHERE status = 'responsive'"
    ).fetchone()["count"]

    return jsonify(
        {
            "total_clients": total_clients,
            "online_clients": online_clients,
        }
    )


@app.route("/api/settings", methods=["GET"])
@auth_required
def get_settings():
    db = get_db()
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    return jsonify({row["key"]: row["value"] for row in rows})


@app.route("/api/settings", methods=["PUT"])
@auth_required
def update_settings():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    db = get_db()
    for key, value in data.items():
        db.execute(
            "UPDATE settings SET value = ? WHERE key = ?",
            (str(value), key),
        )
    db.commit()

    return jsonify({"message": "Settings updated"})


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True, port=5001)

import hashlib
import os
import sqlite3

from flask import Flask, g, jsonify, request, session
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32).hex())
CORS(app, supports_credentials=True)

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
            name TEXT NOT NULL,
            company TEXT NOT NULL,
            email TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active',
            revenue REAL NOT NULL DEFAULT 0
        )
    """
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

    session["user_id"] = user["id"]
    session["username"] = user["username"]

    return jsonify({"username": user["username"]})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@app.route("/api/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"username": session["username"]})


@app.route("/api/change-password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401

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
        "SELECT * FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if hash_password(current_password, user["salt"]) != user["password_hash"]:
        return jsonify({"error": "Current password is incorrect"}), 401

    new_salt = os.urandom(32).hex()
    new_hash = hash_password(new_password, new_salt)
    db.execute(
        "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
        (new_hash, new_salt, session["user_id"]),
    )
    db.commit()

    return jsonify({"message": "Password updated successfully"})


@app.route("/api/clients", methods=["GET"])
def get_clients():
    db = get_db()
    clients = db.execute("SELECT * FROM clients ORDER BY name").fetchall()
    return jsonify([dict(row) for row in clients])


@app.route("/api/stats", methods=["GET"])
def get_stats():
    db = get_db()
    total_clients = db.execute("SELECT COUNT(*) as count FROM clients").fetchone()[
        "count"
    ]
    active_clients = db.execute(
        "SELECT COUNT(*) as count FROM clients WHERE status = 'Active'"
    ).fetchone()["count"]
    total_revenue = (
        db.execute("SELECT COALESCE(SUM(revenue), 0) as total FROM clients").fetchone()[
            "total"
        ]
    )

    return jsonify(
        {
            "total_clients": total_clients,
            "active_clients": active_clients,
            "total_revenue": total_revenue,
        }
    )


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True, port=5001)

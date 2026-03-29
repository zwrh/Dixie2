import atexit
import datetime
import hashlib
import logging
import os
import sqlite3
from functools import wraps

import jwt
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_cors import CORS

from ping import ping, ping_batch
from send_cmd import send_command

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

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
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS ping_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            total_clients INTEGER NOT NULL,
            responsive INTEGER NOT NULL
        )
    """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL,
            timestamp TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS command_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command_id INTEGER NOT NULL,
            identifier TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (command_id) REFERENCES command_history(id)
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
    clients = db.execute(
        "SELECT * FROM clients ORDER BY last_seen DESC NULLS LAST, identifier ASC"
    ).fetchall()
    return jsonify([dict(row) for row in clients])


@app.route("/api/clients", methods=["POST"])
@auth_required
def add_client():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    required = ["identifier", "system_type", "ip_address", "target_port"]
    missing = [f for f in required if not data.get(f) and data.get(f) != 0]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    identifier = str(data["identifier"]).strip()
    system_type = str(data["system_type"]).strip()
    ip_address = str(data["ip_address"]).strip()

    if not identifier or len(identifier) > 64:
        return jsonify({"error": "Identifier must be 1-64 characters"}), 400

    if system_type not in ("Windows", "Linux"):
        return jsonify({"error": "System type must be Windows or Linux"}), 400

    # Validate IP address format
    import re
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip_address):
        return jsonify({"error": "Invalid IP address format"}), 400
    octets = ip_address.split(".")
    if any(int(o) > 255 for o in octets):
        return jsonify({"error": "Invalid IP address: octets must be 0-255"}), 400

    try:
        target_port = int(data["target_port"])
    except (ValueError, TypeError):
        return jsonify({"error": "Port must be a number"}), 400
    if target_port < 1 or target_port > 65535:
        return jsonify({"error": "Port must be between 1 and 65535"}), 400

    db = get_db()
    try:
        db.execute(
            """INSERT INTO clients (identifier, system_type, ip_address, target_port)
               VALUES (?, ?, ?, ?)""",
            (identifier, system_type, ip_address, target_port),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Client with this identifier already exists"}), 409

    return jsonify({"message": "Client added"}), 201


@app.route("/api/clients/<int:client_id>", methods=["GET"])
@auth_required
def get_client(client_id):
    db = get_db()
    client = db.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    if not client:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(dict(client))


@app.route("/api/clients/<int:client_id>", methods=["PUT"])
@auth_required
def update_client(client_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    db = get_db()
    client = db.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    if not client:
        return jsonify({"error": "Client not found"}), 404

    allowed = ["identifier", "system_type", "ip_address", "target_port"]
    updates = {k: data[k] for k in allowed if k in data}
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [client_id]

    try:
        db.execute(f"UPDATE clients SET {set_clause} WHERE id = ?", values)
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Client with this identifier already exists"}), 409

    return jsonify({"message": "Client updated"})


@app.route("/api/clients/<int:client_id>", methods=["DELETE"])
@auth_required
def delete_client(client_id):
    db = get_db()
    result = db.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    db.commit()
    if result.rowcount == 0:
        return jsonify({"error": "Client not found"}), 404
    return jsonify({"message": "Client deleted"})


@app.route("/api/clients/command", methods=["POST"])
@auth_required
def send_client_command():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    identifiers = data.get("identifiers")
    command = data.get("command", "").strip()

    if not identifiers or not isinstance(identifiers, list):
        return jsonify({"error": "identifiers must be a non-empty list"}), 400
    if not command:
        return jsonify({"error": "command is required"}), 400

    # Deduplicate identifiers
    identifiers = list(dict.fromkeys(identifiers))

    db = get_db()
    placeholders = ",".join("?" for _ in identifiers)
    clients = db.execute(
        f"SELECT identifier, ip_address, target_port FROM clients WHERE identifier IN ({placeholders})",
        identifiers,
    ).fetchall()

    found = {c["identifier"] for c in clients}
    not_found = [i for i in identifiers if i not in found]
    if not_found:
        return jsonify({"error": f"Unknown identifiers: {', '.join(not_found)}"}), 404

    results = []
    for client in clients:
        try:
            send_command(client["ip_address"], client["target_port"], command)
            results.append({"identifier": client["identifier"], "status": "sent"})
        except OSError as e:
            results.append({"identifier": client["identifier"], "status": "failed", "error": str(e)})

    # Log command to history
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cursor = db.execute(
        "INSERT INTO command_history (command, timestamp) VALUES (?, ?)",
        (command, now),
    )
    command_id = cursor.lastrowid
    for r in results:
        db.execute(
            "INSERT INTO command_results (command_id, identifier, status) VALUES (?, ?, ?)",
            (command_id, r["identifier"], r["status"]),
        )
    db.commit()

    return jsonify({"results": results})


@app.route("/api/command-history", methods=["GET"])
@auth_required
def get_command_history():
    db = get_db()
    rows = db.execute(
        "SELECT id, command, timestamp FROM command_history ORDER BY id DESC"
    ).fetchall()

    entries = []
    for row in rows:
        results = db.execute(
            "SELECT identifier, status FROM command_results WHERE command_id = ?",
            (row["id"],),
        ).fetchall()
        entries.append({
            "id": row["id"],
            "command": row["command"],
            "timestamp": row["timestamp"],
            "recipients": [r["identifier"] for r in results],
            "results": [{"identifier": r["identifier"], "status": r["status"]} for r in results],
        })

    return jsonify(entries)


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
    total_commands = db.execute(
        "SELECT COUNT(*) as count FROM command_history"
    ).fetchone()["count"]

    return jsonify(
        {
            "total_clients": total_clients,
            "online_clients": online_clients,
            "total_commands": total_commands,
        }
    )


@app.route("/api/contact-rate", methods=["GET"])
@auth_required
def contact_rate():
    range_param = request.args.get("range", "month")

    modifiers = {
        "day": "-1 day",
        "week": "-7 days",
        "month": "-30 days",
        "year": "-365 days",
    }

    db = get_db()
    if range_param in modifiers:
        rows = db.execute(
            "SELECT timestamp, total_clients, responsive FROM ping_log "
            "WHERE timestamp >= datetime('now', ?) ORDER BY timestamp ASC",
            (modifiers[range_param],),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT timestamp, total_clients, responsive FROM ping_log "
            "ORDER BY timestamp ASC"
        ).fetchall()

    return jsonify(
        [
            {
                "timestamp": row["timestamp"],
                "total": row["total_clients"],
                "responsive": row["responsive"],
            }
            for row in rows
        ]
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

    if "ping_interval" in data:
        scheduler.reschedule_job(
            "ping_clients", trigger="interval", seconds=int(data["ping_interval"])
        )

    return jsonify({"message": "Settings updated"})


logger = logging.getLogger(__name__)


def ping_clients():
    """Ping all clients using a single socket and update their status in the database."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    clients = db.execute("SELECT id, identifier, ip_address FROM clients").fetchall()

    if not clients:
        logger.debug("No clients to ping")
        return

    identifiers = [c["identifier"] for c in clients]
    logger.debug("Running ping checks on %d clients: %s", len(clients), ", ".join(identifiers))

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    ip_list = [c["ip_address"] for c in clients]
    results = ping_batch(ip_list)

    for client in clients:
        ip = client["ip_address"]
        reachable = results.get(ip)
        logger.debug(
            "Ping %s (%s): %s", client["identifier"], ip,
            "responsive" if reachable else "non-responsive",
        )
        if reachable:
            db.execute(
                "UPDATE clients SET status = 'responsive', last_seen = ? WHERE id = ?",
                (now, client["id"]),
            )
        else:
            db.execute(
                "UPDATE clients SET status = 'non-responsive' WHERE id = ?",
                (client["id"],),
            )

    # Log this ping cycle
    responsive_count = db.execute(
        "SELECT COUNT(*) FROM clients WHERE status = 'responsive'"
    ).fetchone()[0]
    db.execute(
        "INSERT INTO ping_log (timestamp, total_clients, responsive) VALUES (?, ?, ?)",
        (now, len(clients), responsive_count),
    )
    db.commit()
    db.close()


def get_ping_interval():
    """Read the ping interval from settings."""
    db = sqlite3.connect(DATABASE)
    row = db.execute(
        "SELECT value FROM settings WHERE key = 'ping_interval'"
    ).fetchone()
    db.close()
    return int(row[0]) if row else 30


scheduler = BackgroundScheduler()
atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)


def start_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
    interval = get_ping_interval()
    logger.debug("Starting scheduler with ping interval: %d seconds", interval)
    scheduler.add_job(
        ping_clients,
        "interval",
        seconds=interval,
        id="ping_clients",
        replace_existing=True,
    )
    scheduler.start()


with app.app_context():
    init_db()
    # Avoid double scheduler when Flask reloader is active
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        logger.debug("Scheduler guard passed, starting scheduler...")
        start_scheduler()
    else:
        logger.debug("Skipping scheduler start (reloader parent process)")


if __name__ == "__main__":
    app.run(debug=True, port=5001)

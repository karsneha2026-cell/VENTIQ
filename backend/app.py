
from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from database import get_db_connection, init_db

app = Flask(__name__)
CORS(app)

# Initialize the database
init_db()


@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to VENTIQ Backend!",
        "status": "running"
    })


@app.route("/api/events", methods=["GET"])
def get_events():
    connection = get_db_connection()

    events = connection.execute(
        "SELECT * FROM events ORDER BY event_date"
    ).fetchall()

    connection.close()

    return jsonify([dict(event) for event in events])


@app.route("/api/events", methods=["POST"])
def add_event():
    data = request.get_json(silent=True) or {}

    required_fields = [
        "title", "category", "event_date", "location", "price"
    ]

    if any(field not in data for field in required_fields):
        return jsonify({"error": "Missing required event fields"}), 400

    try:
        price = float(data["price"])
    except (TypeError, ValueError):
        return jsonify({"error": "Price must be a number"}), 400

    if price < 0:
        return jsonify({"error": "Price cannot be negative"}), 400

    try:
        connection = get_db_connection()

        cursor = connection.execute(
            """
            INSERT INTO events
                (title, category, event_date, location, price)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(data["title"]).strip(),
                str(data["category"]).strip(),
                str(data["event_date"]).strip(),
                str(data["location"]).strip(),
                price
            )
        )

        connection.commit()
        event_id = cursor.lastrowid
        connection.close()

        return jsonify({
            "message": "Event added successfully",
            "id": event_id
        }), 201

    except Exception:
        return jsonify({"error": "Could not save the event"}), 500

@app.route("/api/bookings", methods=["POST"])
def create_booking():
    data = request.get_json(silent=True) or {}

    required_fields = [
        "event_id",
        "customer_name",
        "customer_email",
        "tickets"
    ]

    if any(field not in data for field in required_fields):
        return jsonify({"error": "All booking fields are required"}), 400

    try:
        event_id = int(data["event_id"])
        tickets = int(data["tickets"])
    except (TypeError, ValueError):
        return jsonify({"error": "Event ID and tickets must be numbers"}), 400

    customer_name = str(data["customer_name"]).strip()
    customer_email = str(data["customer_email"]).strip()

    if event_id < 1 or tickets < 1:
        return jsonify({"error": "Event ID and tickets must be positive"}), 400

    if not customer_name or not customer_email:
        return jsonify({"error": "Name and email are required"}), 400

    connection = get_db_connection()

    try:
        event = connection.execute(
            "SELECT * FROM events WHERE id = ?",
            (event_id,)
        ).fetchone()

        if event is None:
            return jsonify({"error": "Event not found"}), 404

        if tickets > event["available_tickets"]:
            return jsonify({"error": "Not enough tickets available"}), 400

        total_price = tickets * event["price"]

        connection.execute(
            """
            INSERT INTO bookings
                (event_id, customer_name, customer_email, tickets, total_price)
            VALUES (?, ?, ?, ?, ?)
            """,
            (event_id, customer_name, customer_email, tickets, total_price)
        )

        connection.execute(
            """
            UPDATE events
            SET available_tickets = available_tickets - ?
            WHERE id = ?
            """,
            (tickets, event_id)
        )

        connection.commit()

        return jsonify({
            "message": "Booking successful!",
            "event": event["title"],
            "tickets": tickets,
            "total_price": total_price
        }), 201

    except Exception:
        connection.rollback()
        app.logger.exception("Booking failed")
        return jsonify({"error": "Could not complete booking"}), 500

    finally:
        connection.close()
        
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    if not name or not email or not isinstance(password, str):
        return jsonify({"error": "Name, email and password are required"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    if len(name) > 100 or len(email) > 254:
        return jsonify({"error": "Name or email is too long"}), 400

    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        return jsonify({"error": "Please enter a valid email address"}), 400

    connection = get_db_connection()

    try:
        existing_user = connection.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()

        if existing_user:
            return jsonify({"error": "An account with this email already exists"}), 409

        password_hash = generate_password_hash(password)

        connection.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (name, email, password_hash)
        )

        connection.commit()

        return jsonify({
            "message": "Account created successfully! You can now log in."
        }), 201

    except Exception:
        connection.rollback()
        app.logger.exception("Registration failed")
        return jsonify({"error": "Could not create your account"}), 500

    finally:
        connection.close()


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    if not email or not isinstance(password, str) or not password:
        return jsonify({"error": "Email and password are required"}), 400

    connection = get_db_connection()

    try:
        user = connection.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if user is None or not check_password_hash(
            user["password_hash"], password
        ):
            return jsonify({"error": "Invalid email or password"}), 401

        return jsonify({
            "message": f"Welcome back, {user['name']}!",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        }), 200

    finally:
        connection.close()

if __name__ == "__main__":
    app.run(debug=True)


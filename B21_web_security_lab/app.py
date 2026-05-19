from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)


# Database helper
def get_db():
    return sqlite3.connect("database.db")


# Routes
@app.route("/")
def home():
    return "Server is running"


# Serve login page
@app.route("/login_page")
def login_page():
    return render_template("login.html")


# Serve dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# SQL Injection (intentional for lab)
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(force=True)

        username = data.get("username")
        password = data.get("password")

        conn = get_db()
        cursor = conn.cursor()

        # vulnerable
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)

        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "fail"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# Insecure Direct Object Reference 
@app.route("/user/<int:user_id>")
def get_user(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(f"SELECT id, username, password FROM users WHERE id={user_id}")
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"id": user[0], "username": user[1], "password": user[2]})
    else:
        return jsonify({"error": "User not found"}), 404


# Stored XSS 
@app.route("/comment", methods=["POST"])
def comment():
    data = request.get_json(force=True)
    comment = data.get("comment")

    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO comments(text) VALUES(?)", (comment,))
    # cursor.execute(f"INSERT INTO comments(text) VALUES('{comment}')")
    conn.commit()
    conn.close()

    return jsonify({"status": "saved"})


@app.route("/comments")
def get_comments():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT text FROM comments")
    comments = cursor.fetchall()
    conn.close()

    return jsonify([c[0] for c in comments])


# Disable caching (security lab)
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    #print(app.url_map)
    app.run(debug=True)
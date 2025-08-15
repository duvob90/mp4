import os
import sqlite3
from email.message import EmailMessage
import smtplib

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")
DATABASE = os.path.join(app.root_path, "users.db")
serializer = URLSafeTimedSerializer(app.secret_key)


def init_db() -> None:
    """Create the user table if it does not exist."""
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
            """
        )
        conn.commit()


def get_user(email: str):
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, email, password FROM users WHERE email=?", (email,))
        return cur.fetchone()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = generate_password_hash(request.form["password"])
        try:
            with sqlite3.connect(DATABASE) as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (email, password) VALUES (?, ?)", (email, password)
                )
                conn.commit()
            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered.")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = get_user(email)
        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.")
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        user = get_user(email)
        if user:
            token = serializer.dumps(email, salt="password-reset")
            reset_link = url_for("reset_password", token=token, _external=True)
            send_email(email, "Password reset", f"Use this link to reset: {reset_link}")
        flash("If the email exists, a reset link has been sent.")
        return redirect(url_for("login"))
    return render_template("forgot_password.html")


def send_email(to_email: str, subject: str, body: str) -> None:
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    if not (smtp_server and smtp_user and smtp_password):
        print(f"Email not configured. Reset link for {to_email}: {body}")
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.set_content(body)
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)


@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    try:
        email = serializer.loads(token, salt="password-reset", max_age=3600)
    except (BadSignature, SignatureExpired):
        flash("Invalid or expired token.")
        return redirect(url_for("login"))
    if request.method == "POST":
        password = generate_password_hash(request.form["password"])
        with sqlite3.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET password=? WHERE email=?", (password, email)
            )
            conn.commit()
        flash("Password updated. Please log in.")
        return redirect(url_for("login"))
    return render_template("reset_password.html", token=token)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

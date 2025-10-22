from flask import Flask, render_template, request, redirect, url_for, session, flash
import json, os, random

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session management

DATA_FILE = "suggestions.json"
ADMIN_PASSCODE = "1234"  # 🔐 Change this to whatever you want

# --- Helper functions ---
def ensure_data_file():
    """Ensure the JSON file exists and is valid."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

def load_suggestions():
    ensure_data_file()
    try:
        with open(DATA_FILE, "r") as f:
            data = f.read().strip()
            return json.loads(data) if data else []
    except json.JSONDecodeError:
        return []

def save_suggestions(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def random_id():
    return f"SG-{random.randint(1000, 9999)}"

# --- Routes ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    title = request.form.get("title")
    description = request.form.get("description")

    if not title or not description:
        flash("Please fill out all fields.")
        return redirect(url_for("home"))

    suggestions = load_suggestions()
    suggestions.append({
        "id": random_id(),
        "title": title.strip(),
        "description": description.strip()
    })
    save_suggestions(suggestions)
    flash("✅ Suggestion submitted anonymously!")
    return redirect(url_for("home"))

# --- Admin login ---
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        code = request.form.get("passcode")
        if code == ADMIN_PASSCODE:
            session["is_admin"] = True
            return redirect(url_for("dashboard"))
        else:
            flash("❌ Incorrect passcode.")
            return redirect(url_for("admin"))
    return render_template("admin_login.html")

# --- Dashboard for viewing/clearing suggestions ---
@app.route("/dashboard")
def dashboard():
    if not session.get("is_admin"):
        flash("Access denied. Please log in.")
        return redirect(url_for("admin"))
    suggestions = load_suggestions()
    return render_template("admin_dashboard.html", suggestions=suggestions)

@app.route("/clear", methods=["POST"])
def clear():
    if not session.get("is_admin"):
        flash("Access denied.")
        return redirect(url_for("admin"))
    save_suggestions([])
    flash("🧹 All suggestions cleared.")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    flash("You have been logged out.")
    return redirect(url_for("admin"))

if __name__ == "__main__":
    ensure_data_file()
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import sqlite3, csv, io, datetime

app = Flask(__name__)

# --- DB Setup ---
def init_db():
    conn = sqlite3.connect("typing.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  avg_speed REAL,
                  pauses REAL,
                  backspaces INTEGER,
                  mood TEXT)''')
    conn.commit()
    conn.close()

init_db()


# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    avg_speed = data.get("avg_speed", 0)
    pauses = data.get("avg_pause", 0)
    backspaces = data.get("backspaces", 0)

    # --- Heuristic Rules ---
    if backspaces > 5:
        mood = "Low focus / Distracted"
    elif pauses > 1000:  # ms
        mood = "Thinking mode"
    elif avg_speed < 100:
        mood = "Calm but slow"
    else:
        mood = "High confidence"

    # Save session
    conn = sqlite3.connect("typing.db")
    c = conn.cursor()
    c.execute("INSERT INTO sessions (timestamp, avg_speed, pauses, backspaces, mood) VALUES (?, ?, ?, ?, ?)",
              (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), avg_speed, pauses, backspaces, mood))
    conn.commit()
    conn.close()

    return jsonify({"mood": mood})


@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("typing.db")
    c = conn.cursor()
    c.execute("SELECT * FROM sessions ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return render_template("dashboard.html", sessions=rows)


@app.route("/export")
def export():
    conn = sqlite3.connect("typing.db")
    c = conn.cursor()
    c.execute("SELECT * FROM sessions")
    rows = c.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Timestamp", "Avg Speed", "Pauses", "Backspaces", "Mood"])
    writer.writerows(rows)

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name="typing_sessions.csv")


if __name__ == "__main__":
    app.run(debug=True)

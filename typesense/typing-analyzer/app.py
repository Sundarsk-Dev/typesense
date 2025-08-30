from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import datetime

app = Flask(__name__)
def init_db():
    conn = sqlite3.connect("typing.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    avg_speed REAL,
                    pauses INTEGER,
                    backspaces INTEGER,
                    mood TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    cps = data.get("cps", 0)  # characters per second
    wpm = data.get("wpm", 0)  # words per minute
    pauses = data.get("pauses", 0)  # total pause duration in ms
    backspaces = data.get("backspaces", 0)  # number of corrections

    # --- Weighted Scoring System ---
    score = 0

    # Speed contribution
    if wpm > 70:
        score += 3
    elif wpm > 50:
        score += 2
    elif wpm > 30:
        score += 1
    else:
        score -= 1  # slow typing might indicate carefulness

    # Consistency contribution (pauses)
    if pauses > 2000:
        score -= 2  # too many/long pauses → overthinking or distraction
    elif pauses > 1000:
        score -= 1
    else:
        score += 1  # smooth flow

    # Accuracy contribution (backspaces)
    if backspaces > 10:
        score -= 3  # struggling a lot
    elif backspaces > 5:
        score -= 2
    elif backspaces > 2:
        score -= 1
    else:
        score += 1  # confident and accurate

    # Flow contribution (CPS)
    if cps > 5:
        score += 2
    elif cps > 3:
        score += 1
    elif cps < 1:
        score -= 1
        
    if score >= 5:
        mood = "High confidence & Flow"
    elif 2 <= score < 5:
        mood = "Balanced & Steady"
    elif -1 <= score < 2:
        mood = "Calm / Careful"
    elif -3 <= score < -1:
        mood = "Distracted or Hesitant"
    else:
        mood = "Low focus / Struggling"

    conn = sqlite3.connect("typing.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO sessions (timestamp, avg_speed, pauses, backspaces, mood) VALUES (?, ?, ?, ?, ?)",
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), wpm, pauses, backspaces, mood)
    )
    conn.commit()
    conn.close()

    return jsonify({"mood": mood, "score": score})


@app.route("/stats")
def stats():
    conn = sqlite3.connect("typing.db")
    c = conn.cursor()
    c.execute("SELECT * FROM sessions ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return render_template("stats.html", rows=rows)


@app.route("/clear")
def clear():
    conn = sqlite3.connect("typing.db")
    c = conn.cursor()
    c.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()
    return redirect(url_for("stats"))

if __name__ == "__main__":
    app.run(debug=True)

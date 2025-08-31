from flask import Flask, render_template, jsonify, request, send_file
import sqlite3
from datetime import datetime
import json
import csv
import io
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

def init_db():
    conn = sqlite3.connect('typing.db')
    c = conn.cursor()
    
    c.execute('DROP TABLE IF EXISTS sessions')
    

    c.execute('''CREATE TABLE sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  duration INTEGER,
                  wpm REAL,
                  corrections INTEGER,
                  total_keystrokes INTEGER,
                  pause_count INTEGER,
                  avg_pause_duration REAL,
                  burst_count INTEGER,
                  mood TEXT,
                  raw_text TEXT,
                  metadata TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    

    duration = data.get('duration', 0)
    keystrokes = data.get('keystrokes', [])
    corrections = data.get('corrections', 0)
    text = data.get('text', '')
    
    words = len(text.split()) if text else 0
    minutes = duration / 60 if duration > 0 else 1
    wpm = round(words / minutes) if minutes > 0 else 0
    
    pauses = []
    bursts = []
    
    for i in range(1, len(keystrokes)):
        time_diff = keystrokes[i]['timestamp'] - keystrokes[i-1]['timestamp']
        if time_diff > 1000:  # Pause > 1 second
            pauses.append(time_diff)
        elif time_diff < 150:  # Fast typing < 150ms
            bursts.append(time_diff)
    
    pause_count = len(pauses)
    avg_pause = sum(pauses) / len(pauses) if pauses else 0
    burst_count = len(bursts)
    
    mood = analyze_mood(wpm, corrections, pause_count, burst_count, len(keystrokes))
    
    save_session(
        duration=duration,
        wpm=wpm,
        corrections=corrections,
        total_keystrokes=len(keystrokes),
        pause_count=pause_count,
        avg_pause_duration=avg_pause,
        burst_count=burst_count,
        mood=mood,
        raw_text=text,
        metadata=json.dumps(data)
    )
    
    return jsonify({
        'wpm': wpm,
        'corrections': corrections,
        'mood': mood,
        'pause_count': pause_count,
        'burst_count': burst_count,
        'confidence_score': calculate_confidence(wpm, corrections, burst_count),
        'focus_score': calculate_focus(corrections, pause_count),
        'suggestion': get_suggestion(wpm, corrections, mood)
    })

def analyze_mood(wpm, corrections, pauses, bursts, total_keys):
    """Heuristic-based mood analysis"""
    
    correction_rate = corrections / total_keys if total_keys > 0 else 0
    
    if correction_rate > 0.15:
        return "Stressed 😰"
    elif pauses > 10:
        return "Thoughtful 🤔"
    elif wpm > 60 and corrections < 3:
        return "Confident 😎"
    elif wpm > 50 and bursts > 20:
        return "Focused 🎯"
    elif wpm < 30:
        return "Relaxed 😌"
    else:
        return "Neutral 😊"

def calculate_confidence(wpm, corrections, bursts):
    """Calculate confidence score (0-100)"""
    score = 50  # Base score
    score += min(wpm / 2, 30)  # WPM contribution (max 30)
    score -= corrections * 3  # Penalty for corrections
    score += min(bursts / 2, 20)  # Burst typing bonus (max 20)
    return max(0, min(100, round(score)))

def calculate_focus(corrections, pauses):
    """Calculate focus score (0-100)"""
    score = 100
    score -= corrections * 5  # Penalty for corrections
    score -= pauses * 2  # Penalty for pauses
    return max(0, min(100, round(score)))

def get_suggestion(wpm, corrections, mood):
    """Generate personalized suggestion"""
    if wpm < 30:
        return "Try a 5-second speed drill to boost your typing speed!"
    elif corrections > 5:
        return "Focus on accuracy with a slow typing exercise."
    elif "Stressed" in mood:
        return "Take a deep breath and try a relaxing typing session."
    elif "Confident" in mood:
        return "Great job! Challenge yourself with a longer text."
    else:
        return "Keep practicing! Consistency is key."

def save_session(duration, wpm, corrections, total_keystrokes, pause_count, 
                avg_pause_duration, burst_count, mood, raw_text, metadata):
    """Save typing session to database"""
    conn = sqlite3.connect('typing.db')
    c = conn.cursor()
    c.execute('''INSERT INTO sessions 
                 (timestamp, duration, wpm, corrections, total_keystrokes, 
                  pause_count, avg_pause_duration, burst_count, mood, raw_text, metadata)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (datetime.now().isoformat(), duration, wpm, corrections, 
               total_keystrokes, pause_count, avg_pause_duration, 
               burst_count, mood, raw_text, metadata))
    conn.commit()
    conn.close()

@app.route('/history')
def get_history():
    """Get typing history"""
    conn = sqlite3.connect('typing.db')
    c = conn.cursor()
    c.execute('''SELECT id, timestamp, duration, wpm, corrections, mood 
                 FROM sessions ORDER BY timestamp DESC LIMIT 20''')
    sessions = []
    for row in c.fetchall():
        sessions.append({
            'id': row[0],
            'timestamp': row[1],
            'duration': row[2],
            'wpm': row[3],
            'corrections': row[4],
            'mood': row[5]
        })
    conn.close()
    return jsonify(sessions)

@app.route('/export-csv')
def export_csv():
    """Export typing history as CSV"""
    conn = sqlite3.connect('typing.db')
    c = conn.cursor()
    c.execute('SELECT * FROM sessions ORDER BY timestamp DESC')
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['ID', 'Timestamp', 'Duration (s)', 'WPM', 'Corrections', 
                    'Total Keystrokes', 'Pause Count', 'Avg Pause Duration', 
                    'Burst Count', 'Mood', 'Text'])
    
    for row in c.fetchall():
        writer.writerow(row[:-1])  # Exclude metadata column
    
    conn.close()
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'typing_history_{datetime.now().strftime("%Y%m%d")}.csv'
    )

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

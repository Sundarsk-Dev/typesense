following project was made as an assignment request from a hiring company:
Discover your typing personality through subconscious pattern analysis

Typesense goes beyond traditional typing speed tests by analyzing your subconscious typing patterns to reveal insights about your focus, stress levels, and confidence while typing. Using advanced heuristics and real-time keystroke analysis, it creates a unique "typing mood profile" for each session.
Show Image
✨ Features
🎯 Smart Pattern Analysis

Real-time keystroke tracking with millisecond precision
Pause detection (identifies thinking patterns)
Burst typing analysis (measures confidence indicators)
Correction rate monitoring (stress level indicators)

🧠 Mood Detection System

Stressed 😰: High correction rate indicates anxiety or pressure
Thoughtful 🤔: Long pauses suggest careful consideration
Confident 😎: Fast, accurate typing shows self-assurance
Focused 🎯: Consistent burst patterns indicate deep concentration
Relaxed 😌: Slow, steady typing suggests calm state
Neutral 😊: Balanced typing patterns

📊 Advanced Analytics

Confidence Score: Algorithm-based assessment (0-100)
Focus Score: Attention level measurement (0-100)
WPM Progress Tracking with interactive charts
Historical trend analysis across all sessions

💾 Data Management

SQLite database for persistent storage
Session history with detailed metrics
CSV export for external analysis
Metadata preservation for advanced insights

🎨 Modern UI/UX

Dark theme with amber accents
Responsive design for all devices
Real-time visual feedback
Smooth animations and transitions

🚀 Quick Start
Prerequisites

Python 3.7 or higher
pip package manager

Installation

Clone the repository
bashgit clone https://github.com/yourusername/typesense.git
cd typesense

Install dependencies
bashpip install flask

Run the application
bashpython app.py

Open your browser
http://127.0.0.1:5000


First Test

Choose a test duration (5s, 10s, or 30s)
Start typing naturally in the text area
Watch real-time metrics update
Get your typing mood analysis!

📁 Project Structure
typesense/
├── app.py              # Flask backend with analysis algorithms
├── typing.db           # SQLite database (created automatically)
├── templates/
│   ├── index.html      # Main typing test interface
│   └── stats.html      # Analytics dashboard
├── static/             # (Optional: for additional CSS/JS)
├── requirements.txt    # Python dependencies
└── README.md          # This file

🔧 Configuration
Database Setup
The SQLite database is automatically created on first run. If you encounter database errors, delete typing.db and restart the app.
Secret Key
For production deployment, change the secret key in app.py:
pythonapp.config['SECRET_KEY'] = 'your-secure-secret-key-here'

📊 API Endpoints
EndpointMethodDescription/GETMain typing test interface/statsGETAnalytics dashboard/analyzePOSTSubmit typing data for analysis/historyGETRetrieve typing session history/export-csvGETDownload history as CSV

🧮 Analysis Algorithms
Mood Detection Heuristics
python# Simplified algorithm overview
correction_rate = corrections / total_keystrokes
if correction_rate > 0.15: mood = "Stressed"
elif pauses > 10: mood = "Thoughtful"
elif wpm > 60 and corrections < 3: mood = "Confident"
# ... additional rules
Confidence Score Calculation

Base Score: 50 points
WPM Bonus: Up to +30 points (0.5 points per WPM)
Correction Penalty: -3 points per correction
Burst Bonus: Up to +20 points for fast typing sequences

Focus Score Calculation

Starting Score: 100 points
Correction Penalty: -5 points per correction
Pause Penalty: -2 points per long pause

🎮 Usage Examples
Basic Typing Test

Visit the homepage
Click "30s Test" for a comprehensive analysis
Type naturally about any topic
Review your typing mood and suggestions

Viewing Analytics

Complete several typing tests
Click "View History" or visit /stats
Analyze your progress over time
Export data for external analysis

Interpreting Results

High corrections + low WPM: Try accuracy-focused exercises
Many pauses: You're a thoughtful typist - embrace it!
Fast bursts + low corrections: You're in the zone!

🛠️ Customization
Adding New Moods
Extend the analyze_mood() function in app.py:
pythondef analyze_mood(wpm, corrections, pauses, bursts, total_keys):
    # Add your custom mood logic here
    if your_condition:
        return "Custom Mood 🎨"
Modifying Scoring
Adjust weights in calculate_confidence() and calculate_focus() functions.
UI Customization

Modify colors in the <style> section of HTML templates
Adjust test durations in the frontend JavaScript
Customize suggestions in the get_suggestion() function

🐛 Troubleshooting
Database Errors
bash# Delete existing database and restart
rm typing.db
python app.py
Missing Dependencies
bashpip install flask
Port Already in Use
bash# Kill process on port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# Or run on different port
python app.py --port 5001
🤝 Contributing

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

Ideas for Contributions

Additional mood detection algorithms
Machine learning integration
Typing game modes
Mobile app version
Advanced statistical analysis
Typing speed improvement recommendations

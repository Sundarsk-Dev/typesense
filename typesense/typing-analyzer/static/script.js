let keystrokes = [];
let backspaces = 0;

document.getElementById("typingBox").addEventListener("keydown", (e) => {
    const now = Date.now();
    if (keystrokes.length > 0) {
        keystrokes.push(now - keystrokes[keystrokes.length - 1]); // interval
    } else {
        keystrokes.push(now);
    }
    if (e.key === "Backspace") {
        backspaces++;
    }
});
function submitData() {
    if (keystrokes.length < 2) return;

    let intervals = keystrokes.slice(1);
    let avg_speed = intervals.reduce((a, b) => a + b, 0) / intervals.length;
    let avg_pause = Math.max(...intervals);

    fetch("/analyze", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            avg_speed: avg_speed,
            avg_pause: avg_pause,
            backspaces: backspaces
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("result").innerText = "Mood: " + data.mood;
        setTimeout(() => {
            window.location.href = "/dashboard";
        }, 1200); // wait 1.2 sec before going to dashboard
    });
}

let keystrokes = [];
let backspaces = 0;
let testDuration = 0;
let timerId;
let testStarted = false;
let startTime;

function setDuration(seconds) {
    testDuration = seconds;
    document.getElementById("typingBox").disabled = false;
    document.getElementById("typingBox").focus();
    document.getElementById("timer").innerText = `Test will run for ${seconds} seconds. Start typing...`;
}

document.getElementById("typingBox").addEventListener("keydown", (e) => {
    if (!testStarted && testDuration > 0) {
        startTest();
    }
    if (e.key === "Backspace") {
        backspaces++;
    }
    keystrokes.push(Date.now());
});

function startTest() {
    testStarted = true;
    startTime = Date.now();
    let remaining = testDuration;
    document.getElementById("timer").innerText = `${remaining}s remaining`;

    timerId = setInterval(() => {
        remaining--;
        document.getElementById("timer").innerText = `${remaining}s remaining`;
        if (remaining <= 0) {
            clearInterval(timerId);
            finishTest();
        }
    }, 1000);
}
function finishTest() {
    document.getElementById("typingBox").disabled = true;

    let totalChars = keystrokes.length;
    let elapsedSeconds = testDuration;

    let cps = totalChars / elapsedSeconds;
    let wpm = (totalChars / 5) / (elapsedSeconds / 60); // 1 word ~ 5 chars

    fetch("/analyze", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            cps: cps,
            wpm: wpm,
            backspaces: backspaces,
            pauses: calculatePauses()
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("result").innerText = "Mood: " + data.mood;
        setTimeout(() => {
            window.location.href = "/stats";  // ✅ FIXED HERE
        }, 1200);
    });
}


function calculatePauses() {
    if (keystrokes.length < 2) return 0;
    let intervals = [];
    for (let i = 1; i < keystrokes.length; i++) {
        intervals.push(keystrokes[i] - keystrokes[i-1]);
    }
    return Math.max(...intervals);
}

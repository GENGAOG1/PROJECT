from flask import Flask, render_template_string, request, jsonify, session
import sys
import io
import traceback

app = Flask(__name__)
app.secret_key = "supersecretkey"  # For session

HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Hackermovie Terminal</title>
<style>
body{
    margin:0;
    background:#000;
    color:#00ff00;
    font-family:Consolas, monospace;
    overflow:hidden;
}

canvas{
    position:fixed;
    top:0;
    left:0;
    width:100%;
    height:100%;
    z-index:0;
}

#terminal{
    position:absolute;
    top:20px;
    left:20px;
    width:90%;
    z-index:2;
    text-shadow:0 0 8px #00ff00;
    font-size:18px;
    max-height: 85vh;
    overflow-y: auto;
}

.cursor{
    animation:blink 1s infinite;
    display: inline-block;
}

@keyframes blink{
    50%{ opacity:0; }
}

.scanlines{
    position:fixed;
    inset:0;
    pointer-events:none;
    background:repeating-linear-gradient(transparent 0px, rgba(255,255,255,0.03) 2px, transparent 4px);
    z-index:3;
    mix-blend-mode: overlay;
}

#password-screen {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 10;
    text-align: center;
    background: rgba(0,0,0,0.9);
    padding: 40px;
    border: 1px solid #00ff00;
    box-shadow: 0 0 30px #00ff00;
    display: none;
}

input {
    background: #000;
    color: #00ff00;
    border: 1px solid #00ff00;
    padding: 10px;
    font-family: Consolas, monospace;
    font-size: 18px;
    width: 300px;
}
</style>
</head>

<body>

<canvas id="matrix"></canvas>

<div id="password-screen">
    <h1>SECURE ACCESS TERMINAL</h1>
    <p>ENTER PASSWORD</p>
    <input type="password" id="password-input" autofocus>
    <div id="error" style="color:#ff0000; margin-top:10px;"></div>
</div>

<div id="terminal" style="display:none;">
    <pre id="output"></pre>
    <span id="prompt">root@matrix:~$ </span><input type="text" id="command-input" style="background:transparent;border:none;color:#00ff00;font-family:Consolas,monospace;font-size:18px;outline:none;width:70%;">
</div>

<div class="scanlines"></div>

<script>
// Matrix Rain
const canvas = document.getElementById("matrix");
const ctx = canvas.getContext("2d");

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$%&@█▓▒░01";
const fontSize = 16;
let columns = Math.floor(canvas.width / fontSize);
let drops = new Array(columns).fill(1);

function draw() {
    ctx.fillStyle = "rgba(0,0,0,0.08)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#00ff00";
    ctx.font = `${fontSize}px monospace`;
    for (let i = 0; i < drops.length; i++) {
        const text = chars[Math.floor(Math.random() * chars.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
    }
}
setInterval(draw, 35);

// Terminal logic
const output = document.getElementById("output");
const commandInput = document.getElementById("command-input");
const passwordScreen = document.getElementById("password-screen");
const terminal = document.getElementById("terminal");

let authenticated = false;
const correctPassword = "matrix123"; // Change this

// Show password screen
passwordScreen.style.display = "block";

document.getElementById("password-input").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        const pwd = this.value;
        if (pwd === correctPassword) {
            authenticated = true;
            passwordScreen.style.display = "none";
            terminal.style.display = "block";
            output.innerHTML += "ACCESS GRANTED. Welcome Operator.<br><br>";
            commandInput.focus();
        } else {
            document.getElementById("error").textContent = "ACCESS DENIED";
            setTimeout(() => { document.getElementById("error").textContent = ""; }, 1500);
            this.value = "";
        }
    }
});

// Command handling
commandInput.addEventListener("keypress", async function(e) {
    if (e.key === "Enter" && authenticated) {
        const cmd = this.value.trim();
        if (!cmd) return;

        output.innerHTML += `<span style="color:#00cc00;">root@matrix:~$ ${cmd}</span><br>`;
        
        try {
            const response = await fetch('/execute', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: cmd})
            });
            const data = await response.json();
            
            if (data.output) output.innerHTML += data.output.replace(/\n/g, '<br>') + "<br>";
            if (data.error) output.innerHTML += `<span style="color:#ff4444;">${data.error}</span><br>`;
        } catch(err) {
            output.innerHTML += "Connection error.<br>";
        }

        output.scrollTop = output.scrollHeight;
        this.value = "";
    }
});

// Boot animation
setTimeout(() => {
    if (!authenticated) {
        output.innerHTML = "SYSTEM LOCKED. PASSWORD REQUIRED.<br>";
    }
}, 800);
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/execute", methods=["POST"])
def execute():
    if "authenticated" not in session:
        return jsonify({"error": "Not authenticated"}), 403
    
    command = request.json.get("command", "")
    if not command:
        return jsonify({"error": "No command"})
    
    # Safe Python execution sandbox
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output
    
    try:
        # Restricted globals for safety
        allowed_globals = {
            "__builtins__": {
                "print": print,
                "range": range,
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "list": list,
                "dict": dict,
                "sum": sum,
                "max": max,
                "min": min,
            }
        }
        exec(command, allowed_globals)
        output = redirected_output.getvalue()
        return jsonify({"output": output})
    except Exception as e:
        error = traceback.format_exc()
        return jsonify({"error": str(e) + "\n" + error})
    finally:
        sys.stdout = old_stdout

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

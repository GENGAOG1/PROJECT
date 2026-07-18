from flask import Flask, render_template_string, request, jsonify
import sys, io, traceback, os, math, random

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Hackermovie Terminal</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
<style>
body{margin:0;background:#000;color:#00ff00;font-family:Consolas,monospace;overflow:hidden;}
canvas{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;}
#terminal{position:absolute;top:20px;left:20px;right:20px;bottom:20px;z-index:2;text-shadow:0 0 8px #00ff00;font-size:18px;overflow-y:auto;display:block;}
#input-line{display:flex;align-items:center;}
.scanlines{position:fixed;inset:0;pointer-events:none;background:repeating-linear-gradient(transparent 0px,rgba(255,255,255,0.03) 2px,transparent 4px);z-index:3;}
input{background:transparent;color:#00ff00;border:none;outline:none;font-family:Consolas,monospace;font-size:18px;flex:1;}
</style>
</head>
<body>
<canvas id="matrix"></canvas>

<div id="terminal">
    <pre id="output"></pre>
    <div id="input-line">
        <span style="color:#00cc00;white-space:nowrap;">root@matrix:~$ </span>
        <input type="text" id="command-input" autocomplete="off" autofocus>
    </div>
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
window.addEventListener("resize", resize);

const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$%&@█▓▒░01";
const fontSize = 16;
let columns = Math.floor(canvas.width / fontSize);
let drops = new Array(columns).fill(1);

function draw() {
    ctx.fillStyle = "rgba(0,0,0,0.1)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#00ff00";
    ctx.font = fontSize + "px monospace";
    for (let i = 0; i < drops.length; i++) {
        ctx.fillText(chars[Math.floor(Math.random() * chars.length)], i * fontSize, drops[i] * fontSize);
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
    }
}
setInterval(draw, 35);

// Terminal
const output = document.getElementById("output");
const cmdInput = document.getElementById("command-input");

output.innerHTML = "SYSTEM BOOT COMPLETE<br>Welcome, Operator.<br>Python REPL ready.<br><br>";

// Mobile + Desktop Support
function sendCommand() {
    const cmd = cmdInput.value.trim();
    if (!cmd) return;
    
    output.innerHTML += `<span style="color:#00cc00;">root@matrix:~$ ${cmd}</span><br>`;
    
    fetch("/execute", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({command: cmd})
    })
    .then(r => r.json())
    .then(data => {
        if (data.output) output.innerHTML += data.output.replace(/\n/g, "<br>") + "<br>";
        if (data.error) output.innerHTML += `<span style="color:#ff5555;">${data.error}</span><br>`;
        output.scrollTop = output.scrollHeight;
    })
    .catch(() => {
        output.innerHTML += "<span style='color:#ff5555;'>Connection error.</span><br>";
    });
    
    cmdInput.value = "";
}

// Enter-Taste + Button für Mobile
cmdInput.addEventListener("keypress", e => {
    if (e.key === "Enter") sendCommand();
});

// Extra: Doppelklick auf Input für Mobile
cmdInput.addEventListener("focus", () => {
    cmdInput.scrollIntoView({behavior: "smooth"});
});

setTimeout(() => cmdInput.focus(), 500);
</script

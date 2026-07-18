from flask import Flask, render_template_string, request, jsonify
import sys
import io
import traceback
import os
import math
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"

HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Hackermovie Terminal</title>
<style>
body{margin:0;background:#000;color:#00ff00;font-family:Consolas,monospace;overflow:hidden;}
canvas{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;}
#terminal{position:absolute;top:20px;left:20px;width:90%;z-index:2;text-shadow:0 0 8px #00ff00;font-size:18px;max-height:85vh;overflow-y:auto;display:block;}
.scanlines{position:fixed;inset:0;pointer-events:none;background:repeating-linear-gradient(transparent 0px,rgba(255,255,255,0.03) 2px,transparent 4px);z-index:3;mix-blend-mode:overlay;}
input{background:transparent;color:#00ff00;border:none;outline:none;font-family:Consolas,monospace;font-size:18px;width:80%;}
</style>
</head>
<body>
<canvas id="matrix"></canvas>

<div id="terminal">
    <pre id="output"></pre>
    <span style="color:#00cc00;">root@matrix:~$ </span><input type="text" id="command-input" autocomplete="off" autofocus>
</div>

<div class="scanlines"></div>

<script>
// Matrix Rain
const canvas=document.getElementById("matrix");const ctx=canvas.getContext("2d");
function resize(){canvas.width=window.innerWidth;canvas.height=window.innerHeight;}
resize();window.addEventListener("resize",resize);
const chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$%&@█▓▒░01";const fontSize=16;
let columns=Math.floor(canvas.width/fontSize);let drops=new Array(columns).fill(1);
function draw(){
    ctx.fillStyle="rgba(0,0,0,0.1)";ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle="#00ff00";ctx.font=fontSize+"px monospace";
    for(let i=0;i<drops.length;i++){
        ctx.fillText(chars[Math.floor(Math.random()*chars.length)],i*fontSize,drops[i]*fontSize);
        if(drops[i]*fontSize>canvas.height && Math.random()>0.975) drops[i]=0

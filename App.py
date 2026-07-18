from flask import Flask, render_template_string

app = Flask(__name__)

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
}

.cursor{
    animation:blink 1s infinite;
}

@keyframes blink{
    50%{
        opacity:0;
    }
}

.scanlines{
    position:fixed;
    inset:0;
    pointer-events:none;
    background:repeating-linear-gradient(
        transparent 0px,
        rgba(255,255,255,0.03) 2px,
        transparent 4px
    );
    z-index:3;
}
</style>
</head>

<body>

<canvas id="matrix"></canvas>

<div id="terminal">
<pre id="output"></pre>
<span class="cursor">█</span>
</div>

<div class="scanlines"></div>

<script>

// Matrix Effekt

const canvas=document.getElementById("matrix");
const ctx=canvas.getContext("2d");

canvas.width=window.innerWidth;
canvas.height=window.innerHeight;

const chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$%&@";
const fontSize=16;
const columns=Math.floor(canvas.width/fontSize);

const drops=[];

for(let i=0;i<columns;i++)
    drops[i]=1;

function draw(){

ctx.fillStyle="rgba(0,0,0,0.05)";
ctx.fillRect(0,0,canvas.width,canvas.height);

ctx.fillStyle="#00ff00";
ctx.font=fontSize+"px monospace";

for(let i=0;i<drops.length;i++){

let text=chars[Math.floor(Math.random()*chars.length)];

ctx.fillText(text,i*fontSize,drops[i]*fontSize);

if(drops[i]*fontSize>canvas.height && Math.random()>0.975)
    drops[i]=0;

drops[i]++;

}

}

setInterval(draw,35);


// Terminal Animation

const lines=[

"Initializing...",
"Loading Kernel...",
"Checking Memory...",
"Mounting File Systems...",
"Starting Virtual Services...",
"Loading Graphical Interface...",
"Connecting...",
"Establishing Secure Tunnel...",
"Verifying Encryption...",
"Synchronizing...",
"Downloading Intelligence...",
"Decrypting Archive...",
"Operation Complete.",
"",
"Welcome Operator.",
"",
">"

];

let output=document.getElementById("output");

let line=0;

function write(){

if(line>=lines.length)return;

output.innerHTML+=lines[line]+"\\n";

line++;

setTimeout(write,700);

}

write();

</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(debug=True)

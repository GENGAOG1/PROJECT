from flask import Flask, render_template_string, request, jsonify
import sys
import io
import traceback

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
#password-screen{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);z-index:10;text-align:center;background:rgba(0,0,0,0.95);padding:40px 60px;border:2px solid #00ff00;box-shadow:0 0 40px #00ff00;display:block;}
#terminal{position:absolute;top:20px;left:20px;width:90%;z-index:2;text-shadow:0 0 8px #00ff00;font-size:18px;max-height:85vh;overflow-y:auto;display:none;}
.scanlines{position:fixed;inset:0;pointer-events:none;background:repeating-linear-gradient(transparent 0px,rgba(255,255,255,0.03) 2px,transparent 4px);z-index:3;mix-blend-mode:overlay;}
input{background:#000;color:#00ff00;border:1px solid #00ff00;padding:8px;font-family:Consolas,monospace;font-size:18px;outline:none;}
#error{color:#ff0000;margin-top:15px;}
</style>
</head>
<body>
<canvas id="matrix"></canvas>

<div id="password-screen">
    <h2>SECURE ACCESS REQUIRED</h2>
    <p>ENTER PASSWORD</p>
    <input type="password" id="password-input" autofocus placeholder="********">
    <div id="error"></div>
</div>

<div id="terminal">
    <pre id="output"></pre>
    <span style="color:#00cc00;">root@matrix:~$ </span><input type="text" id="command-input" autocomplete="off">
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
        const text=chars[Math.floor(Math.random()*chars.length)];
        ctx.fillText(text,i*fontSize,drops[i]*fontSize);
        if(drops[i]*fontSize>canvas.height && Math.random()>0.975) drops[i]=0;
        drops[i]++;
    }
}
setInterval(draw,35);

// Terminal
const passwordScreen=document.getElementById("password-screen");
const terminal=document.getElementById("terminal");
const output=document.getElementById("output");
const commandInput=document.getElementById("command-input");
const pwdInput=document.getElementById("password-input");
const errorDiv=document.getElementById("error");
const correctPassword="matrix123";

pwdInput.addEventListener("keypress",e=>{if(e.key==="Enter"){
    if(pwdInput.value===correctPassword){
        passwordScreen.style.display="none";
        terminal.style.display="block";
        output.innerHTML="ACCESS GRANTED<br>System online.<br><br>";
        commandInput.focus();
    } else {
        errorDiv.textContent="ACCESS DENIED";
        pwdInput.value="";
        setTimeout(()=>{errorDiv.textContent="";},1800);
    }
}});

commandInput.addEventListener("keypress",async e=>{if(e.key==="Enter"){
    const cmd=commandInput.value.trim();
    if(!cmd) return;
    output.innerHTML+=`<span style="color:#00cc00;">root@matrix:~$ ${cmd}</span><br>`;
    try{
        const res=await fetch("/execute",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({command:cmd})});
        const data=await res.json();
        if(data.output) output.innerHTML += data.output.replace(/\n/g,"<br>") + "<br>";
        if(data.error) output.innerHTML += `<span style="color:#ff5555;">${data.error}</span><br>`;
    }catch(err){output.innerHTML += "Error executing command.<br>";}
    output.scrollTop=output.scrollHeight;
    commandInput.value="";
}});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/execute", methods=["POST"])
def execute():
    command = request.json.get("command", "")
    if not command:
        return jsonify({"error": "No command"})
    old_stdout = sys.stdout
    redirected = io.StringIO()
    sys.stdout = redirected
    try:
        restricted = {"__builtins__": __builtins__}
        exec(command, restricted)
        return jsonify({"output": redirected.getvalue()})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        sys.stdout = old_stdout

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

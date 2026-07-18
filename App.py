from flask import Flask, render_template, request, jsonify
import sys, io, traceback, os, math, random

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/execute", methods=["POST"])
def execute():
    command = request.json.get("command", "")
    if not command:
        return jsonify({"error": "No command"})

    old_stdout = sys.stdout
    redirected = io.StringIO()
    sys.stdout = redirected

    try:
        local_env = {"os": os, "math": math, "random": random}
        exec(command, {"__builtins__": __builtins__}, local_env)
        return jsonify({"output": redirected.getvalue()})
    except Exception:
        return jsonify({"error": traceback.format_exc()})
    finally:
        sys.stdout = old_stdout

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

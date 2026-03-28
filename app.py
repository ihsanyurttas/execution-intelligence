"""
Minimal Flask API + UI for the Execution Intelligence Engine.
GET  /           → HTML interface
POST /analyze    → accepts canonical payload JSON, returns findings JSON
GET  /scenarios  → lists available scenario files
GET  /scenarios/<name> → returns scenario file content
"""
from __future__ import annotations

import dataclasses
import json
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from engine.detector import detect_patterns
from engine.interpreter import interpret
from engine.output import assemble

app = Flask(__name__)

SCENARIOS_DIR = Path(__file__).parent / "scenarios"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scenarios")
def list_scenarios():
    files = sorted(p.stem for p in SCENARIOS_DIR.glob("*.json"))
    return jsonify(files)


@app.route("/scenarios/<name>")
def get_scenario(name: str):
    path = SCENARIOS_DIR / f"{name}.json"
    if not path.exists():
        return jsonify({"error": "not found"}), 404
    return jsonify(json.loads(path.read_text()))


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({"error": "empty payload"}), 400

        results = detect_patterns(payload)
        findings = [interpret(r) for r in results]
        output = assemble(findings, payload)
        return jsonify(output)

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

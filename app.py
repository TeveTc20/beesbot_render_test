# app.py

from flask import Flask, request, jsonify
from main import agent

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "No message provided"}), 400

    response = agent(message)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

from flask import Flask, request, jsonify, render_template_string
from main import agent
from langchain_core.messages import HumanMessage

app = Flask(__name__)

@app.route("/")
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>BeesBot – Visa Assistant</title>
      <style>
        html, body {
          margin: 0;
          padding: 0;
          height: 100%;
          overflow: hidden;
          font-family: 'Segoe UI', sans-serif;
          background: #f2f4f8;
        }

        .chat-container {
          display: flex;
          flex-direction: column;
          height: 100%;
        }

        .chat-header {
          padding: 12px;
          background-color: #0070f3;
          color: white;
          text-align: center;
          font-weight: bold;
        }

        #chatbox {
          flex: 1;
          overflow-y: auto;
          padding: 12px;
          background-color: #f9f9f9;
        }

        .message {
          max-width: 80%;
          margin: 8px 0;
          padding: 10px 14px;
          border-radius: 16px;
          font-size: 14px;
          line-height: 1.4;
        }

        .user {
          background-color: #0070f3;
          color: white;
          margin-left: auto;
          border-bottom-right-radius: 0;
        }

        .bot {
          background-color: #e5e5ea;
          color: black;
          margin-right: auto;
          border-bottom-left-radius: 0;
        }

        .input-container {
          display: flex;
          padding: 8px;
          background: white;
          border-top: 1px solid #ddd;
        }

        #input {
          flex: 1;
          padding: 10px;
          border-radius: 20px;
          border: 1px solid #ccc;
          font-size: 14px;
          outline: none;
        }

        button {
          margin-left: 8px;
          padding: 0 16px;
          background-color: #0070f3;
          color: white;
          border: none;
          border-radius: 20px;
          font-weight: bold;
          cursor: pointer;
        }
      </style>
    </head>
    <body>
      <div class="chat-container">
        <div class="chat-header">BeesBot – Visa Assistant</div>
        <div id="chatbox"></div>
        <div class="input-container">
          <input id="input" type="text" placeholder="Ask your visa question..." autofocus />
          <button onclick="sendMessage()">Send</button>
        </div>
      </div>

      <script>
        const chatbox = document.getElementById('chatbox');
        const input = document.getElementById('input');

        function appendMessage(sender, text) {
          const div = document.createElement('div');
          div.className = 'message ' + (sender === 'You' ? 'user' : 'bot');
          div.textContent = text;
          chatbox.appendChild(div);
          setTimeout(() => {
            chatbox.scrollTop = chatbox.scrollHeight;
          }, 0);
        }

        async function sendMessage() {
          const msg = input.value.trim();
          if (!msg) return;
          appendMessage('You', msg);
          input.value = '';

          const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
          });
          const data = await res.json();
          appendMessage('Bot', data.response || 'Sorry, no response.');
        }

        input.addEventListener('keypress', function(e) {
          if (e.key === 'Enter') sendMessage();
        });
      </script>
    </body>
    </html>
    """)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "No message provided"}), 400

    # Prepare agent input state
    state = {"messages": [HumanMessage(content=message)]}

    # Call the agent
    result = agent.invoke(state)

    # Extract last message content as reply
    agent_response = ""
    if "messages" in result and result["messages"]:
        agent_response = result["messages"][-1].content

    return jsonify({"response": agent_response})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

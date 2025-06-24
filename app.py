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
        body {
          margin: 0;
          padding: 0;
          font-family: 'Segoe UI', sans-serif;
          background: #f2f4f8;
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
        }
        .chat-container {
          width: 100%;
          max-width: 400px;
          height: 600px;
          background: white;
          box-shadow: 0 4px 20px rgba(0,0,0,0.1);
          border-radius: 12px;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }
        .chat-header {
          padding: 16px;
          background-color: #0070f3;
          color: white;
          font-weight: bold;
          text-align: center;
        }
        #chatbox {
          flex: 1;
          padding: 12px;
          overflow-y: auto;
          background-color: #f9f9f9;
        }
        .message {
          max-width: 75%;
          margin: 8px 0;
          padding: 10px 14px;
          border-radius: 18px;
          clear: both;
          line-height: 1.4;
          font-size: 14px;
        }
        .user {
          background-color: #0070f3;
          color: white;
          align-self: flex-end;
          margin-left: auto;
          border-bottom-right-radius: 0;
        }
        .bot {
          background-color: #e5e5ea;
          color: black;
          align-self: flex-start;
          margin-right: auto;
          border-bottom-left-radius: 0;
        }
        .input-container {
          display: flex;
          padding: 10px;
          border-top: 1px solid #ddd;
          background: #fff;
        }
        #input {
          flex: 1;
          padding: 10px;
          border: 1px solid #ccc;
          border-radius: 20px;
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
          cursor: pointer;
          font-weight: bold;
        }
      </style>
    </head>
    <body>
      <div class="chat-container">
        <div class="chat-header">BeesBot – Visa Assistant</div>
        <div id="chatbox"></div>
        <div class="input-container">
          <input id="input" type="text" placeholder="Ask your visa question..." />
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
          chatbox.scrollTop = chatbox.scrollHeight;
        }

        async function sendMessage() {
          const msg = input.value.trim();
          if (!msg) return;
          appendMessage('You', msg);
          input.value = '';

          try {
            const res = await fetch('/chat', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ message: msg })
            });
            const data = await res.json();
            if (data.response) {
              appendMessage('Bot', data.response);
            } else {
              appendMessage('Bot', 'Sorry, no response.');
            }
          } catch (err) {
            appendMessage('Bot', 'Error reaching the server.');
          }
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

from flask import Flask, request, jsonify, render_template_string
from main import agent
from langchain_core.messages import HumanMessage

app = Flask(__name__)

@app.route("/")
def index():
    # Simple chat UI that calls /chat via fetch POST
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
      <title>AI Chatbot</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        #chatbox { height: 300px; border: 1px solid #ccc; padding: 10px; overflow-y: auto; }
        #input { width: 80%; padding: 8px; }
        button { padding: 8px 12px; }
        .message { margin: 5px 0; }
        .user { font-weight: bold; color: blue; }
        .bot { font-weight: bold; color: green; }
      </style>
    </head>
    <body>
      <h2>AI Chatbot</h2>
      <div id="chatbox"></div>
      <input id="input" type="text" placeholder="Type your message" autofocus />
      <button onclick="sendMessage()">Send</button>

      <script>
        const chatbox = document.getElementById('chatbox');
        const input = document.getElementById('input');

        function appendMessage(sender, text) {
          const div = document.createElement('div');
          div.className = 'message ' + (sender === 'You' ? 'user' : 'bot');
          div.innerHTML = '<span>' + sender + ':</span> ' + text;
          chatbox.appendChild(div);
          chatbox.scrollTop = chatbox.scrollHeight;
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
          if (data.response) {
            appendMessage('Bot', data.response);
          } else {
            appendMessage('Bot', 'Sorry, no response.');
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

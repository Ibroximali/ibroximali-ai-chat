from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from gpt4all import GPT4All

app = Flask(__name__)
CORS(app)  # 🔑 CORS ni yoqamiz

# Modelni tanlash (eng yengil variantni ham qo‘yishingiz mumkin)
model = GPT4All("gpt4all-falcon-q4_0")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    with model.chat_session():
        reply = model.generate(user_input, max_tokens=200).strip()
    return jsonify({"reply": reply})

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    # 🔑 host="0.0.0.0" qo‘yish orqali boshqa qurilmalar ham ulanadi
    app.run(host="0.0.0.0", port=5000)

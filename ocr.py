from flask import Flask, request, jsonify
import requests
import os
import openai
from flask_cors import CORS   # <-- নতুন ইমপোর্ট

app = Flask(__name__)
CORS(app)  # <-- CORS Allow করে দিলাম

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OCR_API_KEY = os.getenv("OCR_API_KEY")
openai.api_key = OPENAI_API_KEY

# ---------- Chatbot ----------
@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.json
    user_input = data.get("message", "")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        answer = response["choices"][0]["message"]["content"]
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- OCR ----------
@app.route("/ocr", methods=["POST"])
def ocr():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    try:
        r = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": file},
            data={"apikey": OCR_API_KEY}
        )
        result = r.json()
        text = result["ParsedResults"][0]["ParsedText"]
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Translator ----------
@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    text = data.get("text", "")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Translate between Bangla and English:\n{text}"}
            ]
        )
        translated = response["choices"][0]["message"]["content"]
        return jsonify({"translation": translated})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "AI Tools Backend by SHADOW JOKER is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

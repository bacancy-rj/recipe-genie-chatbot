"""
Flask web server exposing the recipe chatbot as a simple chat UI and a
JSON API. Each browser session gets its own ChatSession (server-side,
in-memory) so follow-up questions like "tell me more about recipe 2"
work in context.

Run: python3 -m app.server
Then open http://127.0.0.1:5000
"""
import uuid

from flask import Flask, jsonify, render_template, request, session

from .chatbot import ChatSession
from .recommender import RecipeRecommender

app = Flask(__name__)
app.secret_key = "dev-secret-key-recipe-chatbot"  # fine for a local prototype

_recommender = RecipeRecommender()
_sessions = {}


def _get_session():
    sid = session.get("sid")
    if sid is None or sid not in _sessions:
        sid = str(uuid.uuid4())
        session["sid"] = sid
        _sessions[sid] = ChatSession(recommender=_recommender)
    return _sessions[sid]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True) or {}
    message = data.get("message", "")
    chat_session = _get_session()
    reply = chat_session.handle(message)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True, port=5000)

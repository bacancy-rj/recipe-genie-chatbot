import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.chatbot import ChatSession
from app.recommender import RecipeRecommender


def test_recommend_returns_relevant_recipe():
    rec = RecipeRecommender()
    results = rec.recommend(["paneer", "tomato", "butter", "cream"], top_k=3)
    titles = [r["recipe"]["title"] for r in results]
    assert "Paneer Butter Masala" in titles


def test_diet_filter_excludes_non_matching():
    rec = RecipeRecommender()
    results = rec.recommend(["chicken", "onion"], diet="vegetarian", top_k=10)
    for r in results:
        assert "vegetarian" in [d.lower() for d in r["recipe"]["diet"]]


def test_cuisine_filter():
    rec = RecipeRecommender()
    results = rec.recommend(["rice", "soy sauce"], cuisine="Chinese", top_k=10)
    for r in results:
        assert r["recipe"]["cuisine"] == "Chinese"


def test_max_minutes_filter():
    rec = RecipeRecommender()
    results = rec.recommend(["chicken"], max_minutes=30, top_k=10)
    for r in results:
        assert r["recipe"]["ready_in_minutes"] <= 30


def test_synonym_normalization():
    rec = RecipeRecommender()
    normalized = rec.normalize_ingredients(["Tomatoes", "Cottage Cheese", "Onions"])
    assert normalized == ["tomato", "paneer", "onion"]


def test_chat_session_end_to_end():
    session = ChatSession()
    reply = session.handle("I have paneer, tomato, butter and cream")
    assert "Paneer Butter Masala" in reply

    detail = session.handle("tell me more about recipe 1")
    assert "Steps:" in detail


def test_chat_session_diet_and_time_filters():
    session = ChatSession()
    reply = session.handle("vegan curry with chickpeas under 30 minutes")
    assert "chickpeas" in reply.lower() or "chana" in reply.lower() or "picks" in reply.lower()


def test_help_command():
    session = ChatSession()
    reply = session.handle("help")
    assert "ingredients" in reply.lower()

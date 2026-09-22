"""
Core recommendation engine: ingredient-based recipe retrieval using
TF-IDF vectorization + cosine similarity over the recipe knowledge base,
with hard filters for diet, cuisine and cooking time.
"""
import json
import os
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "recipes.json")

# A small synonym map so casual user phrasing ("tomatoes", "paneer cheese")
# lines up with the normalized ingredient vocabulary used in the dataset.
SYNONYMS = {
    "tomatoes": "tomato",
    "onions": "onion",
    "potatoes": "potato",
    "eggplants": "eggplant",
    "aubergine": "eggplant",
    "brinjal": "eggplant",
    "capsicum": "bell pepper",
    "bell peppers": "bell pepper",
    "peppers": "bell pepper",
    "cottage cheese": "paneer",
    "garbanzo beans": "chickpeas",
    "garbanzos": "chickpeas",
    "chick peas": "chickpeas",
    "spring onions": "spring onion",
    "scallion": "spring onion",
    "scallions": "spring onion",
    "coriander": "coriander powder",
    "egg": "eggs",
    "prawns": "shrimp",
    "prawn": "shrimp",
    "beef mince": "ground beef",
    "minced beef": "ground beef",
    "mince": "ground beef",
    "curd": "yogurt",
    "cheese": "cheese",
}


def _normalize_token(text):
    text = text.strip().lower()
    text = re.sub(r"[^a-z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return SYNONYMS.get(text, text)


def _to_doc(ingredients):
    """Turn a list of ingredient strings into an underscore-joined
    token string, e.g. ['red lentils', 'onion'] -> 'red_lentils onion'."""
    return " ".join(ing.strip().lower().replace(" ", "_") for ing in ingredients)


class RecipeRecommender:
    def __init__(self, data_path=DATA_PATH):
        with open(data_path) as f:
            self.recipes = json.load(f)

        self.corpus = [_to_doc(r["ingredients"]) for r in self.recipes]
        # Each ingredient (possibly multi-word, underscored) is one token,
        # so the default whitespace tokenizer is exactly what we want.
        self.vectorizer = TfidfVectorizer(token_pattern=r"[^\s]+")
        self.matrix = self.vectorizer.fit_transform(self.corpus)

    def normalize_ingredients(self, raw_ingredients):
        return [_normalize_token(i) for i in raw_ingredients if _normalize_token(i)]

    def recommend(self, user_ingredients, diet=None, cuisine=None,
                   max_minutes=None, top_k=5):
        """
        user_ingredients: list of raw ingredient strings the user has.
        diet: optional string, e.g. "vegetarian", "vegan", "gluten-free".
        cuisine: optional string, e.g. "Indian", "Italian".
        max_minutes: optional int, max ready_in_minutes.
        Returns a list of result dicts sorted by relevance.
        """
        norm_ingredients = self.normalize_ingredients(user_ingredients)
        query_doc = _to_doc(norm_ingredients) if norm_ingredients else ""
        query_vec = self.vectorizer.transform([query_doc])
        sims = cosine_similarity(query_vec, self.matrix).flatten()

        user_set = set(norm_ingredients)
        results = []
        for idx, recipe in enumerate(self.recipes):
            if diet and diet.lower() not in [d.lower() for d in recipe["diet"]]:
                continue
            if cuisine and cuisine.lower() != recipe["cuisine"].lower():
                continue
            if max_minutes and recipe["ready_in_minutes"] > max_minutes:
                continue

            recipe_set = set(recipe["ingredients"])
            matched = sorted(user_set & recipe_set)
            missing = sorted(recipe_set - user_set)
            coverage = len(matched) / len(recipe_set) if recipe_set else 0.0

            results.append({
                "recipe": recipe,
                "similarity": float(sims[idx]),
                "matched_ingredients": matched,
                "missing_ingredients": missing,
                "coverage": coverage,
            })

        # Rank primarily by how many of the recipe's ingredients the user
        # already has (coverage), then by TF-IDF similarity as a tiebreaker
        # so distinctive shared ingredients (e.g. "paneer") count for more
        # than common ones (e.g. "onion").
        results.sort(key=lambda r: (r["coverage"], r["similarity"]), reverse=True)
        return results[:top_k]

    def available_cuisines(self):
        return sorted({r["cuisine"] for r in self.recipes})

    def available_diets(self):
        diets = set()
        for r in self.recipes:
            diets.update(r["diet"])
        return sorted(diets)

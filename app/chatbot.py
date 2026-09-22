"""
Conversational layer on top of RecipeRecommender.

Design (RAG-style, no LLM required):
  1. Parse the user's free-text message into structured slots
     (ingredients, diet, cuisine, time budget) with lightweight rules.
  2. Retrieve the top matching recipes from the knowledge base via
     RecipeRecommender (TF-IDF + ingredient-coverage ranking).
  3. Generate a natural-language reply from a template, grounded in the
     retrieved recipes (titles, matched/missing ingredients, steps).

This keeps the bot fully deterministic and explainable, and avoids any
dependency on an external LLM API/key for the retrieval + response step.
"""
import re

from .recommender import RecipeRecommender

STOPWORDS = {
    "i", "have", "some", "a", "an", "the", "and", "with", "want", "to",
    "make", "recipe", "recipes", "for", "of", "please", "can", "you",
    "suggest", "recommend", "me", "got", "leftover", "leftovers", "in",
    "my", "fridge", "pantry", "cook", "cooking", "something", "using",
    "also", "under", "over", "within", "curry", "dish", "meal", "any",
    "quick", "fast", "food", "dinner", "lunch", "breakfast", "snack",
}

# Longest alternatives first: Python tries regex alternation left-to-right,
# so "minutes" must precede "min" or it would only consume the "min" prefix.
TIME_RE = re.compile(r"(\d+)\s*(?:minutes|mins|min)\b")

CUISINE_ALIASES = {
    "indian": "Indian", "italian": "Italian", "mexican": "Mexican",
    "chinese": "Chinese", "thai": "Thai", "mediterranean": "Mediterranean",
    "american": "American", "asian": "Asian",
}

DIET_ALIASES = {
    "vegetarian": "vegetarian", "veg": "vegetarian",
    "vegan": "vegan",
    "gluten free": "gluten-free", "gluten-free": "gluten-free",
    "non vegetarian": "non-vegetarian", "non-vegetarian": "non-vegetarian",
    "nonveg": "non-vegetarian", "non veg": "non-vegetarian", "meat": "non-vegetarian",
}


class ChatSession:
    def __init__(self, recommender=None):
        self.recommender = recommender or RecipeRecommender()
        self.last_results = []
        # Known ingredient phrases (from the dataset + synonym aliases),
        # longest phrase first, so greedy matching prefers "red lentils"
        # over matching "lentils" alone.
        from .recommender import SYNONYMS as _SYN
        vocab = set()
        for recipe in self.recommender.recipes:
            vocab.update(recipe["ingredients"])
        vocab.update(_SYN.keys())
        self._vocab_phrases = sorted(vocab, key=lambda p: len(p.split()), reverse=True)

    def _extract_time(self, text):
        m = TIME_RE.search(text)
        if m:
            return int(m.group(1))
        if "quick" in text or "fast" in text:
            return 25
        return None

    def _extract_cuisine(self, text):
        for alias, canonical in CUISINE_ALIASES.items():
            if alias in text:
                return canonical
        return None

    def _extract_diet(self, text):
        # check longer aliases first so "non vegetarian" beats "vegetarian"
        for alias in sorted(DIET_ALIASES, key=len, reverse=True):
            if alias in text:
                return DIET_ALIASES[alias]
        return None

    def _extract_ingredients(self, text, cuisine, diet):
        cleaned = text
        if cuisine:
            cleaned = re.sub(r"\b" + re.escape(cuisine.lower()) + r"\b", " ", cleaned)
        cleaned = TIME_RE.sub(" ", cleaned)
        for alias in DIET_ALIASES:
            cleaned = re.sub(r"\b" + re.escape(alias) + r"\b", " ", cleaned)
        cleaned = re.sub(r"[^a-z\s,]", " ", cleaned)

        # Greedily match known ingredient phrases anywhere in the text
        # (handles free-form sentences, not just comma-separated lists),
        # longest phrases first so multi-word ingredients aren't split up.
        found = []
        for phrase in self._vocab_phrases:
            pattern = r"\b" + re.escape(phrase) + r"\b"
            if re.search(pattern, cleaned):
                found.append(phrase)
                cleaned = re.sub(pattern, " ", cleaned)

        # Anything left over (not comma/and-joined ingredient lists we
        # already consumed above) is treated word-by-word as a fallback,
        # so unseen ingredients still get passed through to the recommender.
        parts = re.split(r"[,]|\band\b", cleaned)
        for part in parts:
            words = [w for w in part.strip().split() if w not in STOPWORDS and len(w) > 2]
            if words:
                found.append(" ".join(words))

        return [i for i in found if i]

    def _looks_like_detail_request(self, text):
        return bool(re.search(r"(recipe|option|number)?\s*#?\s*([1-9])\b", text)
                     and any(w in text for w in ["more", "detail", "step", "instructions", "how"]))

    def _extract_choice_index(self, text):
        m = re.search(r"#?\s*([1-9])\b", text)
        if m:
            return int(m.group(1)) - 1
        return None

    def handle(self, message):
        text = message.strip().lower()

        if text in {"help", "?"}:
            return self._help_text()

        if text in {"list cuisines", "cuisines"}:
            return "Available cuisines: " + ", ".join(self.recommender.available_cuisines())

        if text in {"list diets", "diets"}:
            return "Available diet filters: " + ", ".join(self.recommender.available_diets())

        if self.last_results and self._looks_like_detail_request(text):
            idx = self._extract_choice_index(text)
            if idx is not None and 0 <= idx < len(self.last_results):
                return self._format_detail(self.last_results[idx])

        diet = self._extract_diet(text)
        cuisine = self._extract_cuisine(text)
        minutes = self._extract_time(text)
        ingredients = self._extract_ingredients(text, cuisine, diet)

        if not ingredients:
            return ("Tell me what ingredients you have (e.g. \"I have paneer, "
                    "tomato and onion\"), and optionally a cuisine, diet "
                    "(vegetarian/vegan/gluten-free), or time limit. Type "
                    "'help' for more options.")

        results = self.recommender.recommend(
            ingredients, diet=diet, cuisine=cuisine, max_minutes=minutes, top_k=5,
        )
        self.last_results = results
        return self._format_results(ingredients, results, diet, cuisine, minutes)

    def _format_results(self, ingredients, results, diet, cuisine, minutes):
        if not results:
            filters = []
            if diet:
                filters.append(f"diet={diet}")
            if cuisine:
                filters.append(f"cuisine={cuisine}")
            if minutes:
                filters.append(f"<= {minutes} min")
            filter_note = f" with filters ({', '.join(filters)})" if filters else ""
            return (f"I couldn't find a good match for {', '.join(ingredients)}"
                    f"{filter_note}. Try removing a filter or adding more "
                    f"ingredients.")

        lines = [f"Based on {', '.join(ingredients)}, here are my top picks:\n"]
        for i, r in enumerate(results, 1):
            recipe = r["recipe"]
            pct = round(r["coverage"] * 100)
            lines.append(
                f"{i}. {recipe['title']} ({recipe['cuisine']}, "
                f"{recipe['ready_in_minutes']} min, {recipe['difficulty']}) "
                f"— you already have {pct}% of the ingredients."
            )
            if r["missing_ingredients"]:
                lines.append(f"   Missing: {', '.join(r['missing_ingredients'])}")
        lines.append("\nAsk \"tell me more about recipe 1\" (or 2, 3...) for full steps.")
        return "\n".join(lines)

    def _format_detail(self, result):
        recipe = result["recipe"]
        steps = "\n".join(f"  {i}. {s}" for i, s in enumerate(recipe["steps"], 1))
        return (
            f"{recipe['title']} — {recipe['cuisine']} | {recipe['ready_in_minutes']} min "
            f"| serves {recipe['servings']} | {recipe['difficulty']}\n"
            f"Ingredients: {', '.join(recipe['ingredients'])}\n"
            f"Steps:\n{steps}"
        )

    def _help_text(self):
        return (
            "I recommend recipes based on the ingredients you have.\n"
            "Try: \"I have chicken, tomato and onion\"\n"
            "Add filters: \"vegan curry with chickpeas under 30 minutes\"\n"
            "Commands: 'list cuisines', 'list diets', 'tell me more about recipe 2'"
        )

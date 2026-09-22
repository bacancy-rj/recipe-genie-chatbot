# Recipe Genie — Ingredient-Based Recipe Recommendation Chatbot

A domain-specific chatbot that recommends recipes based on the ingredients
a user already has, plus optional cuisine, diet, and time constraints.
Built as a prototype for the "Build Your Own Domain-Specific Chatbot" task.

## Problem statement

Given a free-text message like:

> "I have paneer, tomato, butter and cream"

or

> "vegan curry with chickpeas under 30 minutes"

recommend the recipes from a knowledge base that the user can cook with what
they have (or the closest match), explain what's missing, and let the user
drill into full step-by-step instructions.

## Approach

This is a **retrieval-based** chatbot (not an LLM-generated one), so it is
fully deterministic, explainable, and needs no external API key:

1. **Knowledge source** — `data/recipes.json`, a curated set of 45 recipes
   across 8 cuisines (Indian, Italian, Mexican, Chinese, Thai, Mediterranean,
   American, Asian) with normalized ingredient lists, diet tags
   (vegetarian/vegan/gluten-free/non-vegetarian), cook time, and full steps.
   Built by `data/build_dataset.py`.

2. **NLU (slot extraction)** — `app/chatbot.py` parses the user's free text
   with lightweight rules/regex to pull out: ingredients, diet, cuisine, and
   a time budget ("under 30 minutes", "quick"). A synonym map normalizes
   casual phrasing ("tomatoes" → "tomato", "cottage cheese" → "paneer").

3. **Retrieval / ranking** — `app/recommender.py`:
   - Each recipe's ingredient list is vectorized with **TF-IDF**
     (`scikit-learn`), so common ingredients (onion, garlic) are
     down-weighted relative to distinctive ones (paneer, shrimp, tofu).
   - The user's ingredients are vectorized the same way and compared to
     every recipe with **cosine similarity**.
   - Results are filtered by any diet/cuisine/time constraints, then ranked
     primarily by **ingredient coverage** (what fraction of the recipe's
     ingredients the user already has) with TF-IDF similarity as a
     tiebreaker — so the top result is genuinely cookable, not just
     topically similar.

4. **Response generation** — retrieved recipes are grounded into a templated,
   natural-language reply (a lightweight form of RAG: retrieve, then
   generate from the retrieved facts, not from a language model). The user
   can ask "tell me more about recipe 2" for full ingredients and steps.

5. **Interfaces** — a Flask web chat UI (`app/server.py` +
   `app/templates/index.html`) and a terminal chat (`cli.py`) share the same
   `ChatSession` / `RecipeRecommender` core.

## Architecture

```
data/build_dataset.py   -> data/recipes.json   (knowledge base)
app/recommender.py      -> TF-IDF + cosine similarity + filters + ranking
app/chatbot.py          -> NLU (slot extraction) + templated response generation
app/server.py           -> Flask web app (chat UI), one ChatSession per browser session
app/templates/index.html-> minimal chat front-end (fetch -> /api/chat)
cli.py                  -> terminal chat, same ChatSession core
tests/test_recommender.py -> unit + end-to-end tests
```

## Running it

```bash
pip install -r requirements.txt
python3 data/build_dataset.py   # regenerate data/recipes.json (already committed)

# Web chat UI
python3 -m app.server
# open http://127.0.0.1:5000

# or terminal chat
python3 cli.py
```

Run tests:

```bash
pytest
```

## Example conversation

```
You: I have paneer, tomato, butter and cream
Recipe Genie: Based on paneer, tomato, butter, cream, here are my top picks:

1. Paneer Butter Masala (Indian, 35 min, medium) — you already have 44% of the ingredients.
   Missing: cashew, garam masala, garlic, ginger, onion
...
Ask "tell me more about recipe 1" (or 2, 3...) for full steps.

You: tell me more about recipe 1
Recipe Genie: Paneer Butter Masala — Indian | 35 min | serves 4 | medium
Ingredients: paneer, tomato, butter, cream, onion, garlic, ginger, garam masala, cashew
Steps:
  1. Saute onion, garlic and ginger until soft.
  ...
```

## Key learnings / design decisions

- **Coverage-first ranking beats pure cosine similarity** for "what can I
  cook" style queries: a recipe that shares 90% of its ingredients with the
  user's pantry is more useful than one that is topically similar but needs
  five more items. TF-IDF similarity is kept as a tiebreaker so distinctive
  matches (e.g. "paneer") still outrank recipes that only share generic
  aromatics (onion, garlic).
- **No LLM dependency** was a deliberate choice for the prototype: retrieval
  + templated generation is fully deterministic, testable, and explainable
  (every recommendation shows exactly which ingredients matched/are
  missing), which matters for a recommendation use case.
- **A synonym map** was necessary almost immediately — real users say
  "tomatoes"/"cottage cheese"/"capsicum" rather than the dataset's
  normalized terms, so exact-string matching alone missed obvious matches.
- **Session-scoped chat state** (server-side, keyed by a cookie) was needed
  so a natural follow-up like "tell me more about recipe 2" works without
  the client re-sending prior results.

## Possible extensions

- Swap the curated JSON for a larger public dataset (e.g. Food.com/RecipeNLG)
  behind the same `RecipeRecommender` interface.
- Add fuzzy/embedding-based ingredient matching (e.g. sentence-transformers)
  instead of the manual synonym map.
- Add an LLM as an optional generation layer on top of the same retrieval
  step for more natural phrasing, while keeping retrieval as the source of
  truth to avoid hallucinated recipes.

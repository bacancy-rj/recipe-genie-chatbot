# Recipe Genie (Next.js) — Ingredient-Based Recipe Recommendation Chatbot

A chatbot that recommends recipes based on the ingredients a user already
has, plus optional cuisine, diet, and time constraints. This is the
JavaScript/Node rebuild of the original Python prototype, built for a MERN
background: **Next.js 16 (App Router) + Node.js**, all plain JavaScript
(no TypeScript, no Python).

## Stack

- **Next.js 16.3.6** (latest) — App Router, Turbopack
- **Node.js 24 LTS** ("Krypton", the current Active LTS line) — see `.nvmrc`
- **React 19**
- Plain **JavaScript** throughout (no TypeScript)
- **Tailwind CSS 4** for styling
- No database, no external LLM API — fully self-contained and deterministic

> Note on `eslint`: the project intentionally pins `eslint@9.x`, not the
> newer `eslint@10`. `eslint-config-next@16.3.6` declares `eslint: ">=9.0.0"`
> as a peer dependency, but its transitive `@typescript-eslint`/scope-manager
> versions are not actually compatible with ESLint 10 yet — `npm run lint`
> crashes with `scopeManager.addGlobals is not a function` under 10.x. 9.x is
> the version Next.js 16 is actually built and tested against today.

## Problem statement

Given a free-text message like:

> "I have paneer, tomato, butter and cream"

or

> "vegan curry with chickpeas under 30 minutes"

recommend the recipes from a knowledge base the user can cook with what
they have (or the closest match), explain what's missing, and let them
drill into full step-by-step instructions.

## Approach

This is a **retrieval-based** chatbot, not one that calls an LLM — so it's
fully deterministic, explainable, and needs no API key:

1. **Knowledge source** — `lib/recipes.json`: 45 recipes across 8 cuisines
   (Indian, Italian, Mexican, Chinese, Thai, Mediterranean, American, Asian)
   with normalized ingredient lists, diet tags, cook time, and full steps.

2. **NLU (slot extraction)** — `lib/chatbot.js` parses free text with
   regex + a vocabulary of known ingredient phrases (built from the dataset)
   to pull out: ingredients, diet, cuisine, and a time budget ("under 30
   minutes", "quick"). A synonym map normalizes casual phrasing
   ("tomatoes" → "tomato", "cottage cheese" → "paneer"). Multi-word
   ingredients ("red lentils", "bell pepper") are matched greedily before
   single words, so they survive even inside a full sentence with no commas.

3. **Retrieval / ranking** — `lib/recommender.js`:
   - Recipes are ranked primarily by **ingredient coverage**: what fraction
     of the recipe's ingredients the user already has. This directly answers
     "what can I actually cook right now?"
   - Ties are broken by a **weighted similarity** score: each ingredient is
     weighted by how rare it is across the dataset (inverse document
     frequency), so a shared "paneer" counts for more than a shared "onion".
     This is the same idea behind TF-IDF, applied directly to the small
     ingredient vocabulary instead of full free text.
   - Diet / cuisine / max-time constraints are applied as hard filters
     before ranking.

4. **Response generation** — retrieved recipes are grounded into a
   templated, natural-language reply (retrieve-then-generate, not an LLM).
   The user can ask "tell me more about recipe 2" for full ingredients and
   steps; that follow-up is resolved against the previous turn's results,
   held in a server-side session.

5. **Interface** — a single Next.js app: a React chat UI (`app/page.js`)
   calling a Node.js API route (`app/api/chat/route.js`). Each browser gets
   an `httpOnly` session cookie so the "tell me more" follow-up works
   without the client re-sending prior results.

## Architecture

```
lib/recipes.json        -> knowledge base (45 recipes, 8 cuisines)
lib/recommender.js       -> ingredient-weighted similarity + coverage ranking + filters
lib/chatbot.js           -> NLU (slot extraction) + templated response generation + session state
app/api/chat/route.js    -> Node.js (Next.js Route Handler): POST /api/chat, cookie-based session
app/page.js              -> React chat UI (client component)
app/layout.js            -> root layout / metadata
tests/recommender.test.js, tests/chatbot.test.js -> Node's built-in test runner (node:test)
```

## Running it

Requires Node 24 (see `.nvmrc`; run `nvm use` if you have nvm installed).

```bash
npm install

# Dev server (Turbopack)
npm run dev
# open http://localhost:3000

# Production build
npm run build
npm run start
```

Run tests (Node's built-in test runner, no extra dependency):

```bash
npm test
```

Lint:

```bash
npm run lint
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

- **Coverage-first ranking beats pure similarity** for "what can I cook"
  queries: a recipe sharing 90% of its ingredients with the user's pantry
  is more useful than one that's topically similar but needs five more
  items. The rarity-weighted score is kept only as a tiebreaker.
- **No LLM dependency** was deliberate: retrieval + templated generation is
  fully deterministic, testable, and explainable — every recommendation
  shows exactly which ingredients matched or are missing.
- **A synonym map and a greedy multi-word ingredient matcher** were needed
  almost immediately — real users write full sentences ("vegan curry with
  chickpeas under 30 minutes") rather than clean comma-separated lists, and
  say "tomatoes"/"cottage cheese" rather than the dataset's normalized
  terms.
- **Session state lives server-side, keyed by a cookie** (an in-memory
  `Map` in the route handler), so "tell me more about recipe 2" works
  without the client re-sending prior results. This is fine for a
  single-instance dev/demo deployment; a multi-instance production
  deployment would move this to a shared store (Redis, a DB).
- **ESLint 9 vs 10**: adopting the newest version of every dependency isn't
  always correct — `eslint-config-next@16.3.6`'s own transitive deps aren't
  compatible with `eslint@10` yet, so pinning to `eslint@9` here is the
  actually-correct, currently-working pairing, not staleness.

## Possible extensions

- Swap the curated JSON for a larger public dataset (e.g. Food.com/RecipeNLG)
  behind the same `lib/recommender.js` interface.
- Move session storage to Redis/a database for multi-instance deployments.
- Add an LLM as an optional generation layer on top of the same retrieval
  step for more natural phrasing, while keeping retrieval as the source of
  truth to avoid hallucinated recipes.

## History

This repo originally held a Python/Flask + scikit-learn prototype (same
dataset, same recommendation approach). It was rebuilt in this Next.js/Node
stack and replaced the Python version here; the old commits are still in
this repo's git history if you want to compare the two.

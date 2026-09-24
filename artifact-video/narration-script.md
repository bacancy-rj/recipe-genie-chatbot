# Recipe Genie — 2–3 min walkthrough narration

Scope: main branch only (the deterministic Next.js/Node chatbot submitted for
the task). No Python history, no LLM-generation branch.

Estimated length: ~430 words ≈ 2:45–3:00 at a natural speaking pace.
Paste the whole thing as-is into an AI avatar tool (HeyGen / Synthesia / D-ID),
or read it yourself while screen-recording the companion slide deck.

---

Hi — this is Recipe Genie, a domain-specific chatbot I built that recommends
recipes based on the ingredients you already have. The stack is Next.js 16
with the App Router, Node.js 24 LTS, React 19, and Tailwind CSS 4 — all in
plain JavaScript, no TypeScript, and no external AI API. It's fully
self-contained and deterministic.

The goal: given a message like "I have paneer, tomato, butter and cream,"
recommend recipes I can actually cook, explain what's missing, and let me
drill into full steps. I built this as a retrieval-based system — not one
that calls a language model — so every recommendation is explainable,
testable, and exactly reproducible.

Here's how it's built, starting from the first line of code. I scaffolded
a fresh Next.js 16 app, then built the knowledge base: a JSON file of 45
recipes across eight cuisines, each with ingredients, diet tags, cook time,
and full steps. On top of that sits the ranking engine. Recipes are ranked
primarily by ingredient coverage — how much of the recipe you can already
make — with a rarity-weighted similarity score as the tiebreaker, so a
shared "paneer" counts for more than a shared "onion."

On top of that is the conversational layer — a lightweight parser that
pulls ingredients, cuisine, diet, and time limits out of free text using
regex and a known-ingredient vocabulary, with a synonym map so "tomatoes"
or "cottage cheese" map to the dataset's terms. It remembers the last
turn's results, so "tell me more about recipe two," or a refinement like
"only vegetarian," works without repeating the ingredient list. All of
this is exposed through one Node.js API route with a cookie-based session,
and a React chat interface on the front end.

Put together, the flow looks like this: your message goes through the
parser, into the ranking engine against the recipe database, and the
ranked results come back as a plain-language reply — all inside one
request.

Let's see it live. I type: "I have paneer, tomato, butter and cream." It
ranks Paneer Butter Masala first, since I already have 44 percent of its
ingredients, and lists exactly what's missing. Asking "tell me more about
recipe one" pulls the full ingredients and steps. And saying "only
vegetarian" afterward re-ranks the same results by diet, without me
repeating a single ingredient.

The whole thing is covered by a 14-test suite on Node's built-in test
runner, passes lint cleanly, and runs on Node 24 LTS with zero deprecated
dependencies. The full source is on GitHub — link's on screen. Thanks for
watching!

---

## Section timings (for pacing / avatar-tool scene breaks)

| Section | Approx. time | Content |
|---|---|---|
| 1. Intro + stack | 0:00–0:22 | Name, one-liner, full tech stack |
| 2. Problem statement | 0:22–0:42 | Example queries, retrieval-not-LLM framing |
| 3. Build, part 1 | 0:42–1:16 | Scaffold → dataset → ranking engine |
| 4. Build, part 2 | 1:16–1:53 | NLU parser → session memory → API/UI |
| 5. Architecture | 1:53–2:07 | One-request end-to-end flow |
| 6. Live demo | 2:07–2:33 | Real conversation walkthrough |
| 7. Wrap-up | 2:33–2:50 | Tests, lint, GitHub link, thanks |

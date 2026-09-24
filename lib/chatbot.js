/**
 * Conversational layer on top of the recommender.
 *
 * Flow (no external LLM needed):
 *   1. Parse the user's free text into ingredients / diet / cuisine / time
 *      with lightweight rules (regex + a known-ingredient vocabulary).
 *   2. Retrieve the top matching recipes from the JSON knowledge base.
 *   3. Generate a plain-language reply from a template, grounded in the
 *      retrieved recipes (titles, matched/missing ingredients, steps).
 */
import recipesData from "./recipes.json" with { type: "json" };
import { recommend, normalizeIngredients, availableCuisines, availableDiets } from "./recommender.js";

const STOPWORDS = new Set([
  "i", "have", "some", "a", "an", "the", "and", "with", "want", "to",
  "make", "recipe", "recipes", "for", "of", "please", "can", "you",
  "suggest", "recommend", "me", "got", "leftover", "leftovers", "in",
  "my", "fridge", "pantry", "cook", "cooking", "something", "using",
  "also", "under", "over", "within", "curry", "dish", "meal", "any",
  "quick", "fast", "food", "dinner", "lunch", "breakfast", "snack",
]);

// Longest alternatives first: "minutes" must be tried before "min" or the
// regex would only consume the "min" prefix and leave "utes" behind.
const TIME_RE = /(\d+)\s*(?:minutes|mins|min)\b/;

const CUISINE_ALIASES = {
  indian: "Indian", italian: "Italian", mexican: "Mexican",
  chinese: "Chinese", thai: "Thai", mediterranean: "Mediterranean",
  american: "American", asian: "Asian",
};

const DIET_ALIASES = {
  "non vegetarian": "non-vegetarian", "non-vegetarian": "non-vegetarian",
  "gluten free": "gluten-free", "gluten-free": "gluten-free",
  "non veg": "non-vegetarian", nonveg: "non-vegetarian",
  vegetarian: "vegetarian", veg: "vegetarian",
  vegan: "vegan", meat: "non-vegetarian",
};

const SYNONYM_KEYS = [
  "tomatoes", "onions", "potatoes", "eggplants", "aubergine", "brinjal",
  "capsicum", "bell peppers", "peppers", "cottage cheese", "garbanzo beans",
  "garbanzos", "chick peas", "spring onions", "scallion", "scallions",
  "coriander", "egg", "prawns", "prawn", "beef mince", "minced beef",
  "mince", "curd",
];

function escapeRegExp(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function buildVocabPhrases() {
  const vocab = new Set(SYNONYM_KEYS);
  for (const recipe of recipesData) {
    for (const ing of recipe.ingredients) vocab.add(ing);
  }
  // Longest phrases (by word count) first, so "red lentils" is matched
  // before a lone "lentils" would be.
  return [...vocab].sort((a, b) => b.split(" ").length - a.split(" ").length);
}

const VOCAB_PHRASES = buildVocabPhrases();

function extractTime(text) {
  const m = TIME_RE.exec(text);
  if (m) return parseInt(m[1], 10);
  if (text.includes("quick") || text.includes("fast")) return 25;
  return null;
}

function extractCuisine(text) {
  for (const [alias, canonical] of Object.entries(CUISINE_ALIASES)) {
    if (text.includes(alias)) return canonical;
  }
  return null;
}

function extractDiet(text) {
  for (const alias of Object.keys(DIET_ALIASES)) {
    if (new RegExp(`\\b${escapeRegExp(alias)}\\b`).test(text)) {
      return DIET_ALIASES[alias];
    }
  }
  return null;
}

function extractIngredients(text, cuisine) {
  let cleaned = text;
  if (cuisine) {
    cleaned = cleaned.replace(new RegExp(`\\b${escapeRegExp(cuisine.toLowerCase())}\\b`, "g"), " ");
  }
  cleaned = cleaned.replace(TIME_RE, " ");
  for (const alias of Object.keys(DIET_ALIASES)) {
    cleaned = cleaned.replace(new RegExp(`\\b${escapeRegExp(alias)}\\b`, "g"), " ");
  }
  cleaned = cleaned.replace(/[^a-z\s,]/g, " ");

  const found = [];
  for (const phrase of VOCAB_PHRASES) {
    const pattern = new RegExp(`\\b${escapeRegExp(phrase)}\\b`);
    if (pattern.test(cleaned)) {
      found.push(phrase);
      cleaned = cleaned.replace(new RegExp(`\\b${escapeRegExp(phrase)}\\b`, "g"), " ");
    }
  }

  const parts = cleaned.split(/,|\band\b/);
  for (const part of parts) {
    const words = part
      .trim()
      .split(/\s+/)
      .filter((w) => w && !STOPWORDS.has(w) && w.length > 2);
    if (words.length) found.push(words.join(" "));
  }

  return found.filter(Boolean);
}

function looksLikeDetailRequest(text) {
  return (
    /(recipe|option|number)?\s*#?\s*([1-9])\b/.test(text) &&
    ["more", "detail", "step", "instructions", "how"].some((w) => text.includes(w))
  );
}

function extractChoiceIndex(text) {
  const m = /#?\s*([1-9])\b/.exec(text);
  return m ? parseInt(m[1], 10) - 1 : null;
}

function formatResults(ingredients, results, diet, cuisine, minutes) {
  if (!results.length) {
    const filters = [];
    if (diet) filters.push(`diet=${diet}`);
    if (cuisine) filters.push(`cuisine=${cuisine}`);
    if (minutes) filters.push(`<= ${minutes} min`);
    const filterNote = filters.length ? ` with filters (${filters.join(", ")})` : "";
    return `I couldn't find a good match for ${ingredients.join(", ")}${filterNote}. Try removing a filter or adding more ingredients.`;
  }

  const lines = [`Based on ${ingredients.join(", ")}, here are my top picks:\n`];
  results.forEach((r, i) => {
    const { recipe } = r;
    const pct = Math.round(r.coverage * 100);
    lines.push(
      `${i + 1}. ${recipe.title} (${recipe.cuisine}, ${recipe.ready_in_minutes} min, ${recipe.difficulty}) — you already have ${pct}% of the ingredients.`
    );
    if (r.missingIngredients.length) {
      lines.push(`   Missing: ${r.missingIngredients.join(", ")}`);
    }
  });
  lines.push('\nAsk "tell me more about recipe 1" (or 2, 3...) for full steps.');
  return lines.join("\n");
}

function formatDetail(result) {
  const { recipe } = result;
  const steps = recipe.steps.map((s, i) => `  ${i + 1}. ${s}`).join("\n");
  return (
    `${recipe.title} — ${recipe.cuisine} | ${recipe.ready_in_minutes} min | serves ${recipe.servings} | ${recipe.difficulty}\n` +
    `Ingredients: ${recipe.ingredients.join(", ")}\n` +
    `Steps:\n${steps}`
  );
}

function helpText() {
  return (
    "I recommend recipes based on the ingredients you have.\n" +
    'Try: "I have chicken, tomato and onion"\n' +
    'Add filters: "vegan curry with chickpeas under 30 minutes"\n' +
    "Commands: 'list cuisines', 'list diets', 'tell me more about recipe 2'"
  );
}

/**
 * Holds per-conversation state (the last set of recommended recipes) so a
 * follow-up like "tell me more about recipe 2" can resolve against them.
 */
export class ChatSession {
  constructor() {
    this.lastResults = [];
  }

  handle(message) {
    const text = message.trim().toLowerCase();

    if (text === "help" || text === "?") return helpText();
    if (text === "list cuisines" || text === "cuisines") {
      return "Available cuisines: " + availableCuisines().join(", ");
    }
    if (text === "list diets" || text === "diets") {
      return "Available diet filters: " + availableDiets().join(", ");
    }

    if (this.lastResults.length && looksLikeDetailRequest(text)) {
      const idx = extractChoiceIndex(text);
      if (idx !== null && idx >= 0 && idx < this.lastResults.length) {
        return formatDetail(this.lastResults[idx]);
      }
    }

    const diet = extractDiet(text);
    const cuisine = extractCuisine(text);
    const minutes = extractTime(text);
    const ingredients = extractIngredients(text, cuisine);

    if (!ingredients.length) {
      return (
        'Tell me what ingredients you have (e.g. "I have paneer, tomato and onion"), ' +
        "and optionally a cuisine, diet (vegetarian/vegan/gluten-free), or time limit. " +
        "Type 'help' for more options."
      );
    }

    const results = recommend(ingredients, { diet, cuisine, maxMinutes: minutes, topK: 5 });
    this.lastResults = results;
    return formatResults(ingredients, results, diet, cuisine, minutes);
  }
}

export { normalizeIngredients };

/**
 * Core recommendation engine: ingredient-based recipe retrieval.
 *
 * How it scores a recipe against what the user has:
 *  - "coverage": what fraction of the RECIPE's ingredients the user already
 *    has (e.g. user has 4 of the 9 ingredients -> 0.44). This is the main
 *    ranking signal, since it directly answers "what can I actually cook?".
 *  - "similarity": a weighted overlap score where rare ingredients across
 *    the whole dataset (e.g. "paneer", "shrimp") count for more than common
 *    ones (e.g. "onion", "garlic"). This is used as a tiebreaker so two
 *    recipes with the same coverage rank sensibly. It's the same idea as
 *    TF-IDF weighting, done directly on a small ingredient vocabulary
 *    instead of full free-text.
 */
import recipes from "./recipes.json" with { type: "json" };

const SYNONYMS = {
  tomatoes: "tomato",
  onions: "onion",
  potatoes: "potato",
  eggplants: "eggplant",
  aubergine: "eggplant",
  brinjal: "eggplant",
  capsicum: "bell pepper",
  "bell peppers": "bell pepper",
  peppers: "bell pepper",
  "cottage cheese": "paneer",
  "garbanzo beans": "chickpeas",
  garbanzos: "chickpeas",
  "chick peas": "chickpeas",
  "spring onions": "spring onion",
  scallion: "spring onion",
  scallions: "spring onion",
  coriander: "coriander powder",
  egg: "eggs",
  prawns: "shrimp",
  prawn: "shrimp",
  "beef mince": "ground beef",
  "minced beef": "ground beef",
  mince: "ground beef",
  curd: "yogurt",
};

function normalizeToken(raw) {
  const text = raw
    .trim()
    .toLowerCase()
    .replace(/[^a-z\s]/g, "")
    .replace(/\s+/g, " ")
    .trim();
  return SYNONYMS[text] || text;
}

// Document-frequency weight for each ingredient across the dataset: an
// ingredient that appears in few recipes (paneer) gets a higher weight than
// one that appears in most of them (onion, garlic).
function buildIngredientWeights() {
  const docCount = {};
  for (const recipe of recipes) {
    for (const ing of new Set(recipe.ingredients)) {
      docCount[ing] = (docCount[ing] || 0) + 1;
    }
  }
  const weights = {};
  for (const [ing, count] of Object.entries(docCount)) {
    weights[ing] = Math.log(recipes.length / count + 1);
  }
  return weights;
}

const INGREDIENT_WEIGHTS = buildIngredientWeights();

function weightedSimilarity(userSet, recipeIngredients) {
  let score = 0;
  let recipeNorm = 0;
  for (const ing of recipeIngredients) {
    const w = INGREDIENT_WEIGHTS[ing] || 1;
    recipeNorm += w * w;
    if (userSet.has(ing)) score += w * w;
  }
  if (recipeNorm === 0) return 0;
  return score / Math.sqrt(recipeNorm);
}

export function normalizeIngredients(rawIngredients) {
  return rawIngredients.map(normalizeToken).filter(Boolean);
}

/**
 * @param {string[]} userIngredients - raw ingredient strings the user typed
 * @param {{ diet?: string, cuisine?: string, maxMinutes?: number, topK?: number }} opts
 */
export function recommend(userIngredients, opts = {}) {
  const { diet, cuisine, maxMinutes, topK = 5 } = opts;
  const normalized = normalizeIngredients(userIngredients);
  const userSet = new Set(normalized);

  const results = [];
  for (const recipe of recipes) {
    if (diet && !recipe.diet.some((d) => d.toLowerCase() === diet.toLowerCase())) {
      continue;
    }
    if (cuisine && recipe.cuisine.toLowerCase() !== cuisine.toLowerCase()) {
      continue;
    }
    if (maxMinutes && recipe.ready_in_minutes > maxMinutes) {
      continue;
    }

    const recipeSet = new Set(recipe.ingredients);
    const matched = [...userSet].filter((i) => recipeSet.has(i)).sort();
    const missing = [...recipeSet].filter((i) => !userSet.has(i)).sort();
    const coverage = recipeSet.size ? matched.length / recipeSet.size : 0;
    const similarity = weightedSimilarity(userSet, recipe.ingredients);

    results.push({
      recipe,
      coverage,
      similarity,
      matchedIngredients: matched,
      missingIngredients: missing,
    });
  }

  results.sort((a, b) => b.coverage - a.coverage || b.similarity - a.similarity);
  return results.slice(0, topK);
}

export function availableCuisines() {
  return [...new Set(recipes.map((r) => r.cuisine))].sort();
}

export function availableDiets() {
  const diets = new Set();
  for (const r of recipes) for (const d of r.diet) diets.add(d);
  return [...diets].sort();
}

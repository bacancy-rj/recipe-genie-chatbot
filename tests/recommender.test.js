import { test } from "node:test";
import assert from "node:assert/strict";
import { recommend, normalizeIngredients } from "../lib/recommender.js";

test("recommend surfaces the obviously relevant recipe first", () => {
  const results = recommend(["paneer", "tomato", "butter", "cream"], { topK: 3 });
  const titles = results.map((r) => r.recipe.title);
  assert.ok(titles.includes("Paneer Butter Masala"));
});

test("diet filter excludes non-matching recipes", () => {
  const results = recommend(["chicken", "onion"], { diet: "vegetarian", topK: 10 });
  for (const r of results) {
    assert.ok(r.recipe.diet.map((d) => d.toLowerCase()).includes("vegetarian"));
  }
});

test("cuisine filter only returns that cuisine", () => {
  const results = recommend(["rice", "soy sauce"], { cuisine: "Chinese", topK: 10 });
  for (const r of results) {
    assert.equal(r.recipe.cuisine, "Chinese");
  }
});

test("max minutes filter is respected", () => {
  const results = recommend(["chicken"], { maxMinutes: 30, topK: 10 });
  for (const r of results) {
    assert.ok(r.recipe.ready_in_minutes <= 30);
  }
});

test("synonym normalization maps casual phrasing to dataset terms", () => {
  const normalized = normalizeIngredients(["Tomatoes", "Cottage Cheese", "Onions"]);
  assert.deepEqual(normalized, ["tomato", "paneer", "onion"]);
});

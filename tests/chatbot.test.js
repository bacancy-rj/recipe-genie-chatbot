import { test } from "node:test";
import assert from "node:assert/strict";
import { ChatSession } from "../lib/chatbot.js";

test("end to end: recommend then drill into a recipe's steps", () => {
  const session = new ChatSession();
  const reply = session.handle("I have paneer, tomato, butter and cream");
  assert.match(reply, /Paneer Butter Masala/);

  const detail = session.handle("tell me more about recipe 1");
  assert.match(detail, /Steps:/);
});

test("diet and time filters are extracted from free text", () => {
  const session = new ChatSession();
  const reply = session.handle("vegan curry with chickpeas under 30 minutes");
  assert.match(reply, /picks|chickpeas|chana/i);
});

test("help command explains usage", () => {
  const session = new ChatSession();
  const reply = session.handle("help");
  assert.match(reply, /ingredients/i);
});

test("greetings get a friendly reply, not a recipe dump", () => {
  const session = new ChatSession();
  for (const greeting of ["Hi", "hello", "Hey there", "good morning", "Hi buddy"]) {
    const reply = session.handle(greeting);
    assert.match(reply, /recipe genie|cook/i);
    assert.doesNotMatch(reply, /you already have/i);
  }
});

test("thanks and goodbye get short acknowledgements", () => {
  const session = new ChatSession();
  assert.match(session.handle("thanks!"), /welcome/i);
  assert.match(session.handle("bye"), /bye/i);
});

test("off-topic text gets a clarifying reply instead of 0%-match recipes", () => {
  const session = new ChatSession();
  const reply = session.handle("hello bot?");
  assert.match(reply, /recipe assistant|didn't recognize/i);
  assert.doesNotMatch(reply, /you already have/i);
});

test("a real ingredient still works even alongside noise words", () => {
  const session = new ChatSession();
  const reply = session.handle("hi, I have chicken and onion");
  assert.match(reply, /you already have/i);
});

test("a diet-only follow-up refines the previous ingredients instead of failing", () => {
  const session = new ChatSession();
  const first = session.handle(
    "I have 3 tomatoes and 2 onions with few potatoes any quick fancy fast food reciepe?"
  );
  assert.match(first, /you already have/i);
  assert.doesNotMatch(first, /vegetarian/i);

  const refined = session.handle("Provide me only pure-veg recipe");
  assert.match(refined, /you already have/i);
  for (const line of refined.split("\n")) {
    if (!line.trim().match(/^\d+\./)) continue;
    const title = line.replace(/^\d+\.\s*/, "").split(" (")[0];
    const recipe = session.lastResults.find((r) => r.recipe.title === title).recipe;
    assert.ok(recipe.diet.includes("vegetarian") || recipe.diet.includes("vegan"), title);
  }
});

test("a plain diet-only message with no prior context asks for ingredients", () => {
  const session = new ChatSession();
  const reply = session.handle("only vegetarian please");
  assert.match(reply, /tell me what ingredients/i);
});

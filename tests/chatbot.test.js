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

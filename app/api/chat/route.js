import { randomUUID } from "crypto";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { ChatSession } from "@/lib/chatbot";

const SESSION_COOKIE = "recipe_genie_sid";

// In-memory, per-server-process session store. Fine for a single-instance
// dev/demo deployment; a real deployment would move this to a shared store
// (Redis, a DB) since Next.js can run multiple server instances.
const sessions = new Map();

function getSession(sid) {
  if (!sessions.has(sid)) sessions.set(sid, new ChatSession());
  return sessions.get(sid);
}

export async function POST(request) {
  const { message } = await request.json();
  const cookieStore = await cookies();
  let sid = cookieStore.get(SESSION_COOKIE)?.value;
  const isNewSession = !sid;
  if (isNewSession) sid = randomUUID();

  const session = getSession(sid);
  const reply = session.handle(String(message ?? ""));

  const response = NextResponse.json({ reply });
  if (isNewSession) {
    response.cookies.set(SESSION_COOKIE, sid, {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
    });
  }
  return response;
}

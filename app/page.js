"use client";

import { useEffect, useRef, useState } from "react";

const GREETING =
  "Hi! I'm Recipe Genie. Tell me what ingredients you have, and I'll suggest recipes you can make. Type 'help' anytime.";

export default function Home() {
  const [messages, setMessages] = useState([{ who: "bot", text: GREETING }]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const logRef = useRef(null);

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight });
  }, [messages]);

  async function sendMessage(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    setMessages((prev) => [...prev, { who: "user", text }]);
    setInput("");
    setSending(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { who: "bot", text: data.reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { who: "bot", text: "Sorry, something went wrong talking to the server." },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#f4f1ec] flex justify-center p-6">
      <div className="w-full max-w-2xl bg-white rounded-xl shadow-lg flex flex-col h-[85vh] overflow-hidden">
        <header className="bg-[#2f6f4e] text-white px-5 py-4">
          <h1 className="text-lg font-semibold">🍲 Recipe Genie</h1>
          <p className="text-xs opacity-85 mt-1">
            Tell me what&apos;s in your kitchen — I&apos;ll recommend what to cook.
          </p>
        </header>

        <div ref={logRef} className="flex-1 overflow-y-auto px-5 py-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex mb-3.5 ${m.who === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[80%] px-3.5 py-2.5 rounded-xl text-sm leading-relaxed whitespace-pre-wrap ${
                  m.who === "user"
                    ? "bg-[#2f6f4e] text-white rounded-br-sm"
                    : "bg-[#f0efe9] text-gray-900 rounded-bl-sm"
                }`}
              >
                {m.text}
              </div>
            </div>
          ))}
        </div>

        <div className="text-xs text-gray-400 px-5 pb-2">
          Try: &quot;I have chicken, tomato and onion, vegan under 30 minutes&quot;
        </div>

        <form onSubmit={sendMessage} className="flex gap-2 border-t border-gray-100 p-3">
          <input
            type="text"
            autoComplete="off"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="I have paneer, tomato and onion..."
            className="flex-1 px-3 py-2.5 border border-gray-300 rounded-lg text-sm outline-none focus:border-[#2f6f4e]"
          />
          <button
            type="submit"
            disabled={sending}
            className="bg-[#2f6f4e] hover:bg-[#255c40] disabled:opacity-60 text-white rounded-lg px-4 py-2.5 text-sm"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

"""
Terminal chat interface for the Recipe Genie chatbot (no browser needed).

Run: python3 cli.py
"""
from app.chatbot import ChatSession


def main():
    session = ChatSession()
    print("Recipe Genie: Hi! Tell me what ingredients you have (type 'quit' to exit, 'help' for tips).")
    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nRecipe Genie: Bye! Happy cooking.")
            break
        if message.lower() in {"quit", "exit"}:
            print("Recipe Genie: Bye! Happy cooking.")
            break
        reply = session.handle(message)
        print(f"Recipe Genie: {reply}\n")


if __name__ == "__main__":
    main()

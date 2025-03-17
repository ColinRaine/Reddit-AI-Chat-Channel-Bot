import time
import logging
from pw_bot_utils import capture_chat_text
from playwright.sync_api import sync_playwright
from pw_login_utils import login_to_reddit, open_reddit_chat
from pw_followup_utils import handle_followup
from collections import deque
from pw_terminal import print_banner, print_random_quote, start_terminal_progress


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
recent_messages = deque(maxlen=10)  # ✅ Track last 10 messages to prevent duplicate replies

def main():
    start_terminal_progress()

    with sync_playwright() as p:  # ✅ Keep Playwright open for the bot
        browser, page = login_to_reddit(p)
        open_reddit_chat(page)

        print_banner()
        print("\n==============================================================")
        print("🤖  BOT IS RUNNING!  🤖")
        print_random_quote()
        print("==============================================================\n")

        while True:
            try:
                time.sleep(2)  # Pause before checking messages again

                chat_data = capture_chat_text(page)
                message_text = chat_data["message"]
                message_sender = chat_data["sender"]

                # Skip bot's own messages
                if message_sender.lower() == "sparklinggr4pejuice":
                    print("⚠️ Skipping bot's own message.")
                    continue

                # ✅ Check for duplicate messages **before calling handle_followup**
                if message_text in recent_messages:
                    continue  # ✅ Skip duplicate messages

                # ✅ Use follow-up module to check if bot should reply
                if handle_followup(page, message_text, message_sender, recent_messages):
                    continue  # ✅ Follow-up was handled, move to next message

            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(10)


if __name__ == "__main__":
    main()  # ✅ Keep everything inside Playwright context

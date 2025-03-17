import time
from collections import deque
from pw_bot_utils import TRIGGER_WORD, capture_chat_text, send_chat_message
from pw_openai_utils import generate_reply
from playwright.sync_api import sync_playwright
from pw_login_utils import login_to_reddit, open_reddit_chat


def main():
    with sync_playwright() as p:  # ✅ Keep Playwright open for the bot
        browser, page = login_to_reddit(p)  # ✅ Pass Playwright instance
        open_reddit_chat(page)  # ✅ Use the same page instance

        print("\n==============================")
        print("🤖  BOT IS RUNNING!  🤖")
        print("⚡ Waiting for commands... ⚡")
        print("==============================\n")

        recent_messages = deque(maxlen=5)  # Track last 5 messages
        while True:
            try:
                time.sleep(5)  # Pause before checking messages again

                chat_data = capture_chat_text(page)
                message_text = chat_data["message"]
                message_sender = chat_data["sender"]

                # Skip bot's own messages
                if message_sender.lower() == "sparklinggr4pejuice":
                    print("⚠️ Skipping bot's own message.")
                    continue

                # ✅ Check if message contains the trigger word
                if any(word in message_text.lower() for word in TRIGGER_WORD):
                    print(f"🎯 Trigger detected: {message_text}")

                    # ✅ Generate a response
                    response_text = generate_reply(message_text)

                    # ✅ Send the response
                    send_chat_message(page, response_text, message_sender)

                    # ✅ Add to Recent Messages
                    recent_messages.append(message_text)

                    print("\n💬 ====================")
                    print(f"✅ Bot replied:\n{response_text}")
                    print("==================== 💬\n")

            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(10)


if __name__ == "__main__":
    main()  # ✅ Keep everything inside Playwright context
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
import logging

# Define the bot's activation command
TRIGGER_WORD = ["u/sparklinggr4pejuice".lower(), "@sparklinggr4pejuice".lower()]

logging.basicConfig(level=logging.INFO)

def capture_chat_text(page: Page):
    """Extracts the latest chat message and assigns correct senders, handling compact messages properly."""
    try:
        chat_data = page.evaluate("""
            (() => {
                let events = document.querySelector("body > faceplate-app > rs-app").shadowRoot
                    .querySelector("div.container > rs-room-overlay-manager > rs-room").shadowRoot
                    .querySelector("main > rs-timeline").shadowRoot
                    .querySelector("div > rs-virtual-scroll-dynamic").shadowRoot
                    .querySelectorAll("rs-timeline-event");

                if (!events || events.length === 0) {
                    return { "message": "", "sender": "Unknown" };
                }

                let lastKnownSender = null;
                let latestMessage = { "message": "", "sender": "Unknown" };

                // **First Pass: Establish sender history**
                for (let i = 0; i < events.length; i++) {
                    let event = events[i];
                    if (!event || !event.shadowRoot) continue;

                    let usernameElem = event.shadowRoot.querySelector("div > div.flex.flex-col > div > rs-timeline-event-hovercard > span");
                    let username = usernameElem ? usernameElem.innerText.trim() : "Unknown";
                    let isCompact = event.hasAttribute("compact");

                    // Store last known sender for compact messages
                    if (username !== "Unknown") {
                        lastKnownSender = username;
                    } else if (isCompact && lastKnownSender) {
                        username = lastKnownSender;
                    }
                }

                // **Second Pass: Extract latest message with correct sender**
                for (let i = events.length - 1; i >= 0; i--) {
                    let event = events[i];
                    if (!event || !event.shadowRoot) continue;

                    let messageElem = event.shadowRoot.querySelector("div > div.room-message-body > div");
                    let usernameElem = event.shadowRoot.querySelector("div > div.flex.flex-col > div > rs-timeline-event-hovercard > span");

                    let messageText = messageElem ? messageElem.innerText.trim() : "";
                    let username = usernameElem ? usernameElem.innerText.trim() : "Unknown";
                    let isCompact = event.hasAttribute("compact");

                    // Assign last known sender to compact messages
                    if (isCompact && lastKnownSender) {
                        username = lastKnownSender;
                    }

                    if (messageText) {
                        latestMessage = { "message": messageText, "sender": username };
                        break;
                    }
                }

                return latestMessage;
            })();
        """)

        return chat_data  # ✅ Returns extracted message and sender name

    except PlaywrightTimeoutError as e:
        logging.error("Timeout error while capturing chat text: %s", e)
        return {"message": "", "sender": ""}
    except PlaywrightError as e:
        logging.error("Playwright error while capturing chat text: %s", e)
        return {"message": "", "sender": ""}
    except Exception as e:
        logging.error("An unexpected error occurred while capturing chat text: %s", e)
        return {"message": "", "sender": ""}

def send_chat_message(page: Page, text: str, sender: str):
    """Finds the chat input inside Shadow DOM and sends a message using Enter key."""
    try:
        # ✅ Locate the chat input field inside the Shadow DOM
        chat_input_handle = page.evaluate_handle("""
            () => document.querySelector("body > faceplate-app > rs-app")?.shadowRoot
                .querySelector("div.container > rs-room-overlay-manager > rs-room")?.shadowRoot
                .querySelector("main > rs-message-composer")?.shadowRoot
                .querySelector("form > div > rs-textarea-auto-size > textarea")
        """)

        if not chat_input_handle:
            logging.error("Chat input field not found.")
            return

        # ✅ Extract the actual DOM element from the JSHandle
        chat_input = chat_input_handle.as_element()
        if not chat_input:
            logging.error("Failed to extract chat input as element.")
            return

        response_text = f"u/{sender} {text}"

        # ✅ Use Playwright's built-in `fill()` method instead of manual value setting
        chat_input.fill(response_text)
        chat_input.press("Enter")  # ✅ Press Enter after filling the message

    except PlaywrightTimeoutError as e:
        logging.error("Timeout error while sending chat message: %s", e)
    except PlaywrightError as e:
        logging.error("Playwright error while sending chat message: %s", e)
    except Exception as e:
        logging.error("An unexpected error occurred while sending chat message: %s", e)

import time
from collections import deque
from pw_bot_utils import TRIGGER_WORD, send_chat_message
from pw_openai_utils import generate_reply

# ✅ Store conversation history per user
conversation_history = {}  # { "username": deque(["msg1", "msg2", ...]) }

FOLLOW_UP_DURATION = 60  # ✅ Follow-up mode lasts 60 seconds
CONTEXT_LIMIT = 10  # ✅ Number of previous messages bot remembers per user

# ✅ Dictionary to track follow-up mode per user
follow_up_sessions = {}

def handle_followup(page, message_text, message_sender, recent_messages):
    """Handles follow-up mode with memory of recent messages."""

    current_time = time.time()

    # ✅ Initialize user history if not exists
    if message_sender not in conversation_history:
        conversation_history[message_sender] = deque(maxlen=CONTEXT_LIMIT)

    # ✅ Add message to user’s conversation history
    conversation_history[message_sender].append(message_text)

    # ✅ Check if the user is in follow-up mode
    if message_sender in follow_up_sessions:
        start_time = follow_up_sessions[message_sender]
        if current_time - start_time <= FOLLOW_UP_DURATION:
            print(f"💬 Follow-up mode active for {message_sender}")
            # ✅ Small delay inside follow-up mode
            time.sleep(2)
            # ✅ Pass recent conversation history to OpenAI
            context = "\n".join(conversation_history[message_sender])
            response_text = generate_reply(f"Context:\n{context}\n\nUser: {message_text}")

            send_chat_message(page, response_text, message_sender)
            recent_messages.append(message_text)
            print("\n💬 ====================")
            print(f"✅ Bot replied with follow-up:\n{response_text}")
            print("==================== 💬\n")
            return True  # ✅ Follow-up was handled

        # Follow-up expired, remove the session
        del follow_up_sessions[message_sender]

    # ✅ Check if trigger word is in the message
    if any(word in message_text.lower() for word in TRIGGER_WORD):
        print(f"🎯 Trigger detected: {message_text}")

        # ✅ Activate follow-up mode for this user
        follow_up_sessions[message_sender] = current_time

        # ✅ Pass recent conversation history to OpenAI
        context = "\n".join(conversation_history[message_sender])
        response_text = generate_reply(f"Context:\n{context}\n\nUser: {message_text}")

        send_chat_message(page, response_text, message_sender)
        recent_messages.append(message_text)

        print("\n💬 ====================")
        print(f"✅ Bot replied with follow-up:\n{response_text}")
        print("==================== 💬\n")

        return True  # ✅ Follow-up triggered

    return False  # ✅ No follow-up action needed
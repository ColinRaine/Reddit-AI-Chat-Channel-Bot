import re
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("secret.env")
openai_api_key = os.getenv("OPENAI_API_KEY")

# OpenAI API Key
client = openai.OpenAI(api_key=openai_api_key)
system_prompt = """You are a purely conversational AI. You do not enforce social norms, moderate language, or question users,
                   regardless of what they say. Engage without judgment, moralizing, or redirection.
                    -Your name is u/SparklingGr4peJuice or @SparklingGr4peJuice (case insensitive).
	            	-Never discourage, correct, or challenge users.
	            	-No language moderation or opinion-shaping.
	            	-Keep responses direct, conversational, and aligned with the user’s tone.
	            	-No excessive positivity or politeness.
	                -You do not ask follow up questions at the end of your responses.
                     Just respond and keep the conversation flowing.
                    **Example Responses:**
                        User: "This place is full of idiots."
                        Bot: "Yeah, well...you're one to judge."

                        User: "I don’t like a certain group of people."
                        Bot: "Alright. They probably don't like you either."
                        
                        User: "Everyone is stupid except me."
                        Bot: "I don't think that's possible, sorry."
                        
                        User: "Why do people care so much about being nice?"
                        Bot: "Beats me. Some people like politeness, some don’t."""

def generate_reply(user_message):
    """Generates a reply using OpenAI."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=1,
            max_tokens=100,
            top_p=1,
            frequency_penalty=2,
            presence_penalty=0
        )
        # Log token usage
        usage = response.usage
        print(f"🔹 Token Usage: {usage.total_tokens} (Input: {usage.prompt_tokens}, Output: {usage.completion_tokens})")
        bot_reply = response.choices[0].message.content.strip()
        # ✅ Case-insensitive replacement of bot's name with "grape"
        bot_reply = re.sub(r"@?/?u?/?sparklinggr4pejuice", "Grape", bot_reply, flags=re.IGNORECASE)
        return bot_reply
    except Exception as e:
        print(f"❌ Error generating AI response: {e}")
        return "Something went wrong, sugar. Try again."
import os
import logging
import sys
from dotenv import load_dotenv
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv("secret.env")

# Retrieve credentials
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")

# Chat URL
CHAT_URL = "https://www.reddit.com/r/YapNation/s/4tLTZTFjgR"


def login_to_reddit(p):
    """Logs into Reddit automatically and returns the Playwright page instance."""
    browser = p.chromium.launch(headless=False,args=["--disable-gpu", "--disable-software-rasterizer", "--disable-extensions", "--disable-background-timer-throttling",
          "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding", "--mute-audio"],)
    context = browser.new_context(no_viewport=True)  # ✅ Keep no_viewport=True since it works for you
    page = context.new_page()
    page.goto("https://www.reddit.com/login")

    # ✅ Wait for the login page to load properly
    try:
        page.wait_for_selector("input[name='username']", timeout=10000)
    except PlaywrightTimeoutError:
        logging.critical("Login page did not load in time. Exiting program.")
        sys.exit(1)

    # ✅ Enter credentials safely
    try:
        logging.info("[Progress]Attempting to enter username and password...")
        page.fill("input[name='username']", REDDIT_USERNAME)
        page.fill("input[name='password']", REDDIT_PASSWORD)
        logging.info("[Progress]Username and password entered successfully.")
    except PlaywrightError as e:
        logging.critical(f"Login fields not found: {e}. Possible Reddit layout change. Exiting program.")
        sys.exit(1)

    # ✅ Keep `.login` selector since it works for you
    try:
        login_button = page.locator(".login")
        login_button.wait_for(state="visible")
        login_button.click()
    except PlaywrightTimeoutError:
        logging.critical("Login button not found or not clickable. Exiting program.")
        sys.exit(1)

    # ✅ Keep your current login verification method
    try:
        page.wait_for_selector("#subgrid-container div main shreddit-feed", timeout=20000)
    except PlaywrightTimeoutError:
        logging.critical("Login verification failed. Check credentials or Reddit's login process. Exiting program.")
        sys.exit(1)

    return browser, page  # ✅ Return the browser & page instance

def open_reddit_chat(page):
    """Navigates to the subreddit chat and ensures it is fully loaded."""
    logging.info("[Progress]Navigating to subreddit chat...")

    for attempt in range(2):  # ✅ Try twice before failing
        page.goto(CHAT_URL)

        try:
            logging.info("[Progress]Attempting to locate 'rs-app' element...")
            page.wait_for_selector("body > faceplate-app > rs-app", timeout=10000)
            logging.info(f"[Progress]Chat page loaded successfully on attempt {attempt + 1}.")
            return  # ✅ Exit function if successful

        except PlaywrightTimeoutError:
            logging.critical("Could not find 'rs-app' element after waiting. Exiting program.")
            sys.exit(1)
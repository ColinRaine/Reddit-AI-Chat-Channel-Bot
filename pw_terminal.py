import logging
import random
import psutil
import shutil
from tqdm import tqdm  # ✅ Progress bar library

# ✅ Define progress marker and total steps
PROGRESS_MARKER = "[Progress]"
TOTAL_STEPS = 5  # Adjust to match actual startup steps

class LogProgressHandler(logging.Handler):
    """Intercepts logging messages and updates the progress bar dynamically."""
    def __init__(self, total_steps):
        super().__init__()
        self.total_steps = total_steps
        self.progress_bar = None  # ✅ Start uninitialized
        self.detected_steps = 0  # ✅ Track detected progress markers

    def emit(self, record):
        """Check for progress markers and update the progress bar accordingly."""
        log_message = record.getMessage()

        if PROGRESS_MARKER in log_message:
            self.detected_steps += 1
            step_message = log_message.replace(PROGRESS_MARKER, "").strip()

            # ✅ Initialize progress bar only on first log
            if self.progress_bar is None:
                self.progress_bar = tqdm(
                    total=self.total_steps,
                    bar_format="{l_bar}{bar} Step {n_fmt}/{total_fmt} [{elapsed}s]",
                    dynamic_ncols=True,
                    leave=True
                )
            # ✅ Update progress bar with step message
            self.progress_bar.update(1)
            self.progress_bar.set_description(f"Step {self.detected_steps}")

            # ✅ Stop progress bar when all steps complete
            if self.detected_steps >= self.total_steps:
                self.stop()

    def stop(self):
        """Close the progress bar when tracking completes."""
        if self.progress_bar:
            self.progress_bar.close()

def start_terminal_progress():
    """Initializes and attaches the progress tracker to logging."""
    tracker = LogProgressHandler(total_steps=TOTAL_STEPS)
    logging.getLogger().addHandler(tracker)
    return tracker  # ✅ Return the tracker instance to stop later

def print_banner():
    banner = """
           _  _  _                                                               
    _ (_)(_)(_) _                                                            
   (_)         (_)_       _  _  _  _  _       _  _  _  _     _  _  _  _      
   (_)    _  _  _(_)_  _ (_)(_)(_)(_)(_) _   (_)(_)(_)(_)_  (_)(_)(_)(_)_    
   (_)   (_)(_)(_) (_)(_)       _  _  _ (_)  (_)        (_)(_) _  _  _ (_)   
   (_)         (_) (_)        _(_)(_)(_)(_)  (_)        (_)(_)(_)(_)(_)(_)   
   (_) _  _  _ (_) (_)       (_)_  _  _ (_)_ (_) _  _  _(_)(_)_  _  _  _     
      (_)(_)(_)(_) (_)         (_)(_)(_)  (_)(_)(_)(_)(_)    (_)(_)(_)(_)    
                                             (_)                             
                                             (_)                             
    """
    # Get terminal width
    terminal_width = shutil.get_terminal_size().columns

    # Center each line
    centered_banner = "\n".join(line.center(terminal_width) for line in banner.split("\n"))
    print("\033[95m" + centered_banner + "\033[0m")  # purple text

def colored_text(text, color="green"):
    colors = {"red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m", "blue": "\033[94m", "reset": "\033[0m"}
    return f"{colors[color]}{text}{colors['reset']}"

def print_status_bar(messages_handled=0):
    cpu_usage = psutil.cpu_percent()
    mem_usage = psutil.virtual_memory().percent
    print(f"\r🖥 CPU: {cpu_usage}%  💾 RAM: {mem_usage}%  💬 Messages: {messages_handled}", end="", flush=True)

def print_random_quote():
    quotes = [
        "🤖 Beep boop. Ready to serve.",
        "⚡ Initializing... hope I don't become self-aware.",
        "📡 Connected. Awaiting commands.",
        "🧠 Thinking... (not too hard though)",
    ]
    print(random.choice(quotes))
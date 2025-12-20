# Keep this script in the root directory
import os

# Constants
PORT = 3001
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DOWNLOADS_DIR = os.path.join(ROOT_DIR, "downloads")
STATIC_DIR = os.path.join(ROOT_DIR, "static")
TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")

LOG_FILE = os.path.join(ROOT_DIR, "log.txt")
TSV_PATH = os.path.join(DOWNLOADS_DIR, "input.txt")

MONTHS = {
    "jan": "january",
    "feb": "february",
    "mar": "march",
    "apr": "april",
    "may": "may",
    "jun": "june",
    "jul": "july",
    "aug": "august",
    "sep": "september",
    "oct": "october",
    "nov": "november",
    "dec": "december",
}

KEYWORDS = {"font", "front", "back", "symbol", "logo", "image", "color", "birthstone", "box", "faster"}

# Functions
def log(text: str) -> None:
    with open(LOG_FILE, "a") as logs:
        logs.write(text + "\n")
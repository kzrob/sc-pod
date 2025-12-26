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
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03",
    "apr": "04", "april": "04",
    "may": "05", "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12",
}

KEYWORDS = {"font", "front", "back", "symbol", "logo", "image", "color", "birthstone", "box", "faster", "icon", "symbol"}

# Functions
def log(text: str) -> None:
    with open(LOG_FILE, "a") as logs:
        logs.write(text + "\n")
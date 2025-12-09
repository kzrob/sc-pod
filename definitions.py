# Keep this script in the root directory
import os

# Constants
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DOWNLOADS_DIR = os.path.join(ROOT_DIR, "downloads")
TSV_PATH = os.path.join(DOWNLOADS_DIR, "input.txt")

STATIC_DIR = os.path.join(ROOT_DIR, "static")
IMAGES_DIR = os.path.join(STATIC_DIR, "images")

TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")

DATABASE = os.path.join(ROOT_DIR, "data.db")
LOG_FILE = os.path.join(ROOT_DIR, "log.txt")

MONTHS_3 = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
}

# Functions
def log(text: str) -> None:
    with open(LOG_FILE, "a") as logs:
        logs.write(text + "\n")
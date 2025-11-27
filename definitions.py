# Keep this script in the root directory
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DOWNLOADS_DIR = os.path.join(ROOT_DIR, "downloads")
TSV_PATH = os.path.join(DOWNLOADS_DIR, "input.txt")

STATIC_DIR = os.path.join(ROOT_DIR, "static")
IMAGES_DIR = os.path.join(STATIC_DIR, "images")

TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")

DATABASE = os.path.join(ROOT_DIR, "data.db")

MONTHS_3 = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}
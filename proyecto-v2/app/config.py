from dotenv import load_dotenv
import os

load_dotenv()

DEBUG = os.getenv("DEBUG", "True") == "True"
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH")

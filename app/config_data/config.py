import os
from typing import List, Tuple

from dotenv import find_dotenv, load_dotenv

if not find_dotenv():
    msg = "Переменные окружения не загружены, т.к отсутствует файл .env"
    exit(msg)
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("API_KEY")
RAPID_API_URI = "https://aliexpress-ecommerce.p.rapidapi.com/v1/search"
MAX_QUERY_RESULTS = 60  # 1 страница результатов запроса

HEADERS = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "aliexpress-ecommerce.p.rapidapi.com",
}

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
)
DB_PATH = "sqlite+aiosqlite:///./database.db"

custom_commands = []


MIN_DELAY = 0.5
MAX_DELAY = 30
FACTOR = 3
MAX_ATTEMPTS = 5
RANDOMNESS = 0.05


def add_command(command: Tuple[str, str]) -> None:
    custom_commands.append(command)


def get_commands() -> List[Tuple[str, str]]:
    commands = list(DEFAULT_COMMANDS)
    commands.extend(custom_commands)
    return commands

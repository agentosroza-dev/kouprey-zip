import os

from dotenv import load_dotenv


def load_env() -> None:
    base = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.join(base, "..", ".env.local")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

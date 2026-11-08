import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'pantry.db'}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

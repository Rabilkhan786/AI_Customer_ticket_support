"""Load application configuration."""

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"

load_dotenv(PROJECT_ROOT / ".env")


def load_config() -> dict[str, Any]:
    """Load configuration values from config.yaml."""
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


settings = load_config()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
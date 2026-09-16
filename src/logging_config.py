"""Application logging configuration."""

import logging

from src.config import PROJECT_ROOT, settings


def setup_logging() -> None:
    """Set up console and file logging."""

    log_settings = settings["logging"]

    log_file = PROJECT_ROOT / log_settings["file_path"]
    log_file.parent.mkdir(parents=True, exist_ok=True)

    log_level = getattr(
        logging,
        log_settings["level"].upper(),
        logging.INFO,
    )

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                log_file,
                encoding="utf-8",
            ),
        ],
    )
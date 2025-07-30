import asyncio
import logging
import sys
import os

from dotenv import load_dotenv

from xify import Xify
from xify.errors import APIError

load_dotenv()

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configure root logger."""

    """
    Work on this later to include setting up logging to files
    using the platformdirs method of doing things 
    """

    # Determine log levels
    log_values = {10: "DEBUG", 20: "INFO", 30: "WARN", 40: "ERROR", 50: "CRITICAL"}

    console_log_level = logging.DEBUG

    # Set formatter for file and console handlers
    formatter = logging.Formatter(
        "[%(asctime)s] %(name)-35s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure file and console handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_log_level)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(console_handler)

    # Control third-party log levels
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    root_logger.info(
        "Logging configured. File level: %s, Console level: %s",
        None,
        log_values[console_log_level],
    )


async def main():
    try:
        xify_client = Xify(
            consumer_key=os.getenv("CONSUMER_KEY"),
            consumer_secret=os.getenv("CONSUMER_SECRET"),
            access_token=os.getenv("ACCESS_TOKEN"),
            access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
        )

        async with xify_client:
            content = {"msg": "Hello X!"}
            response = await xify_client.tweet(content)

        logger.info("Tweet posted succesfully! ID: %s", response["id"])

    except APIError as e:
        logging.exception("An API error occurred.")
        logging.exception("Full error response from API: %s", e.response)

    except Exception:
        logger.exception("An unexpected error occurred.")


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())

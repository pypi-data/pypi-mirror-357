import asyncio
import logging
import os

from dotenv import load_dotenv

from xify import Xify
from xify.errors import APIError, XifyError

load_dotenv()

# Basic logging to print to the console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def main() -> None:
    """Create a client and post a single tweet."""
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

        logging.info("Tweet posted succesfully! ID: %s", response["id"])

    except APIError as e:
        logging.exception("An API error occurred.")
        logging.exception("Full error response from API: %s", e.response)

    except XifyError:
        logging.exception("A library error occurred.")

    except Exception:
        logging.exception("An unexpected error occurred.")


if __name__ == "__main__":
    asyncio.run(main())

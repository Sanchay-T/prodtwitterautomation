from requests_oauthlib import OAuth1Session
import os
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging configuration
logging.basicConfig(
    filename="twitter_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def tweet_message(message):
    # Get credentials from environment variables
    consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
    consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        error_message = "Missing required OAuth credentials in environment variables"
        logging.error(error_message)
        return error_message

    # Create OAuth1Session for authentication
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    # Prepare the payload (tweet content)
    payload = {"text": message}

    # Make the POST request to Twitter API
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        error_message = (
            f"Error: Request returned an error: {response.status_code} {response.text}"
        )
        logging.error(error_message)
        return error_message

    return json.dumps(response.json(), indent=4, sort_keys=True)

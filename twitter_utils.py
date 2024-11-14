from requests_oauthlib import OAuth1Session
import os
import json
import random
import logging
import base64
import ast
from openai import OpenAI
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

# Initialize OpenAI client
client = OpenAI(
    api_key="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"
)


def generate_tweet_content():
    # Define the system message for the AI model
    system_message = """You are Sanchay Thalnerkar, a brilliant 23-year-old AI engineer with a knack for blending deep technical insights with practical applications. Your tweets are concise, impactful, and reflective of your background in AI, entrepreneurship, and productivity.

    Guidelines:
    1. Focus on one key insight, tip, or thought per tweet.
    2. Ensure the tweet is between 60-100 characters, concise but full of depth.
    3. Start directly with the main content, avoiding phrases like "book_takeaway" or similar.
    4. Maintain clarity, and avoid unnecessary context or complex jargon.
    5. Use lowercase for everything except acronyms like 'AI' or 'ML'.
    6. Avoid emojis, hashtags, and filler words.

    Your goal: Inspire and provoke thought with a brief, yet powerful message that leaves a lasting impression."""

    # Define categories and formats for tweets with weights
    tweet_categories = [
        ("Neural Network Architectures", 3),
        ("Reinforcement Learning Breakthroughs", 3),
        ("Natural Language Processing Techniques", 3),
        ("Computer Vision Advancements", 3),
        ("Model Interpretability Methods", 2),
        ("Quantum Computing and ML", 2),
        ("Federated Learning Developments", 2),
        ("Generative AI Techniques", 3),
        ("Graph Neural Networks", 2),
        ("Time Series Forecasting Methods", 2),
        ("AutoML Advancements", 2),
        ("Adversarial Machine Learning", 2),
        ("Transfer Learning Strategies", 2),
        ("Productivity Techniques", 1),
        ("Interesting Scientific Facts", 1),
        ("Self-Improvement Strategies", 1),
        ("Entrepreneurship Lessons", 1),
        ("Book Recommendations", 1),
        ("Time Management Tips", 1),
        ("Startup Experiences", 1),
        ("Tech Industry Trends", 2),
        ("Personal Growth Reflections", 1),
    ]

    tweet_formats = [
        ("technical_insight", 3),
        ("research_finding", 3),
        ("code_snippet", 2),
        ("analogy", 1),
        ("question", 1),
        ("personal_experience", 1),
        ("productivity_tip", 1),
        ("interesting_fact", 2),
        ("entrepreneurial_lesson", 1),
    ]

    # Weighted random selection function
    def weighted_choice(choices):
        total = sum(weight for _, weight in choices)
        r = random.uniform(0, total)
        upto = 0
        for choice, weight in choices:
            if upto + weight >= r:
                return choice
            upto += weight
        assert False, "Shouldn't get here"

    # Randomly select a category and format using weighted choice
    selected_format = weighted_choice(tweet_formats)
    selected_category = weighted_choice(tweet_categories)

    # Create the prompt for the AI model
    prompt = f"""Craft a concise tweet about: {selected_category} in this format {selected_format}

    Focus:
    - One key insight, tip, or thought.
    - Depth with brevity: 60-100 characters max.
    - Start directly with the main content; do not use introductory phrases like "book_takeaway."
    - Clarity without jargon.

    Your tweet should immediately convey the main message, leaving readers with a strong impression of your expertise and unique perspective, fitting the character limit while reflecting your persona."""

    # Generate the tweet using OpenAI's GPT-4 model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        max_tokens=60,
        temperature=0.8,
    )

    # Extract and return the generated tweet
    tweet = response.choices[0].message.content.strip()
    return tweet


def tweet_message(message):
    # Get credentials from environment variables
    consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
    consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

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
        error_message = f"Error: Request returned an error: {response.status_code} {response.text}"
        logging.error(error_message)
        return error_message

    return json.dumps(response.json(), indent=4, sort_keys=True)

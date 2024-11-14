import os
import time
import random
import logging
import signal
import sys
import pandas as pd
from twitter_utils import tweet_message
from datetime import datetime

# Set up logging configuration
logging.basicConfig(
    filename="twitter_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class TweetTracker:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.load_excel()

    def load_excel(self):
        try:
            self.df = pd.read_excel(self.file_path)
            # Add status columns if they don't exist
            if 'Status' not in self.df.columns:
                self.df['Status'] = 'pending'
            if 'Posted_At' not in self.df.columns:
                self.df['Posted_At'] = None
            self.save_excel()
        except FileNotFoundError:
            logging.error(f"Excel file not found: {self.file_path}")
            raise

    def save_excel(self):
        try:
            self.df.to_excel(self.file_path, index=False)
        except Exception as e:
            logging.error(f"Error saving Excel file: {str(e)}")

    def get_pending_tweets(self):
        return self.df[self.df['Status'] == 'pending']

    def mark_as_posted(self, index):
        self.df.at[index, 'Status'] = 'posted'
        self.df.at[index, 'Posted_At'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_excel()

def format_tweet_content(tweet):
    # Split the tweet into lines
    lines = tweet.split("\n")
    formatted_lines = []

    for line in lines:
        # If line contains a colon, add an extra line break
        if ":" in line and not line.strip().endswith("\n"):
            stripped_line = line.rstrip()
            formatted_lines.append(stripped_line + "\n")
        else:
            # Handle bullet points conversion
            stripped_line = line.lstrip()
            if stripped_line.startswith("-"):
                whitespace = line[: len(line) - len(stripped_line)]
                formatted_line = whitespace + ">" + stripped_line[1:]
                formatted_lines.append(formatted_line)
            else:
                formatted_lines.append(line)

    return "\n".join(formatted_lines)

def get_tweet_interval():
    # Keep random interval between 10-20 minutes
    return random.randint(600, 1200)

def tweet_loop(tweet_tracker):
    pending_tweets = tweet_tracker.get_pending_tweets()
    
    if pending_tweets.empty:
        print("No pending tweets found!")
        logging.info("No pending tweets found!")
        return

    print(f"Found {len(pending_tweets)} pending tweets")
    logging.info(f"Found {len(pending_tweets)} pending tweets")

    for index, row in pending_tweets.iterrows():
        try:
            # Get and format the tweet content
            tweet_content = format_tweet_content(row['Unnamed: 0'])

            print("\nPosting tweet:")
            print(tweet_content)
            print("\nCharacter count: {}".format(len(tweet_content)))

            # Post the tweet
            response = tweet_message(tweet_content)
            print("Twitter API response:", response)
            
            # Mark tweet as posted
            tweet_tracker.mark_as_posted(index)
            
            logging.info(f"Posted tweet: {tweet_content}")
            logging.info(f"Twitter API response: {response}")

        except Exception as e:
            logging.exception("An error occurred during the tweet process")
            print("An error occurred: {}".format(str(e)))
            continue  # Continue to next tweet if there's an error

        # Wait before next tweet if there are more pending
        if index < pending_tweets.index[-1]:
            interval = get_tweet_interval()
            print("\nWaiting for {:.2f} minutes before next tweet".format(interval / 60))
            logging.info(
                "Waiting for {:.2f} minutes before next tweet".format(interval / 60)
            )
            time.sleep(interval)

def signal_handler(signum, frame):
    print("Received signal to terminate. Exiting gracefully...")
    sys.exit(0)

def main():
    print("Twitter bot started")
    logging.info("Twitter bot started")

    # Set up signal handlers for graceful termination
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Initialize tweet tracker
        file_path = "tweets.xlsx"
        tweet_tracker = TweetTracker(file_path)

        # Start tweeting loop
        tweet_loop(tweet_tracker)

    except FileNotFoundError:
        print(f"Excel file not found: {file_path}")
        logging.error(f"Excel file not found: {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        logging.exception("An unexpected error occurred")
    finally:
        print("Twitter bot stopped")
        logging.info("Twitter bot stopped")

if __name__ == "__main__":
    main()

import json
import random
import time
from datetime import datetime
import os
from pathlib import Path

# Topics for our simulated tweets
TOPICS = ["data engineering", "machine learning", "python", "big data", "cloud computing"]
SENTIMENTS = ["positive", "negative", "neutral"]
SENTIMENT_WEIGHTS = [0.6, 0.2, 0.2]  # Most tweets tend to be positive or neutral

class TweetGenerator:
    def __init__(self, output_dir="data/raw"):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_tweet(self):
        """Generate a simulated tweet with random content but realistic structure"""
        topic = random.choice(TOPICS)
        sentiment = random.choices(SENTIMENTS, weights=SENTIMENT_WEIGHTS)[0]
        
        # Generate tweet text based on topic and sentiment
        if sentiment == "positive":
            templates = [
                f"I really love working with {topic}! #tech",
                f"Just discovered an amazing new feature in {topic}. Game changer! #excited",
                f"The latest developments in {topic} are incredible! #impressed"
            ]
        elif sentiment == "negative":
            templates = [
                f"Struggling with {topic} today. So frustrating! #help",
                f"Why is {topic} so complicated? Not a fan right now.",
                f"Disappointed by the new updates to {topic}. #letdown"
            ]
        else:  # neutral
            templates = [
                f"Working on a new {topic} project this weekend.",
                f"Anyone have resources for learning more about {topic}?",
                f"Just read an article about {topic}. Interesting stuff.",
            ]
            
        tweet_text = random.choice(templates)
        
        # Create tweet object with metadata
        tweet = {
            "id": f"tweet_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
            "text": tweet_text,
            "topic": topic,
            "created_at": datetime.now().isoformat(),
            "user": f"user_{random.randint(1000, 9999)}",
            "likes": random.randint(0, 100),
            "retweets": random.randint(0, 20),
            "actual_sentiment": sentiment  # Ground truth (normally we wouldn't have this)
        }
        
        return tweet
    
    def save_tweet(self, tweet):
        """Save a tweet to a JSON file"""
        filename = f"{self.output_dir}/tweet_{tweet['id']}.json"
        with open(filename, 'w') as f:
            json.dump(tweet, f)
        return filename
    
    def generate_stream(self, delay=1.0):
        """Generate a stream of tweets with a delay between each"""
        while True:
            tweet = self.generate_tweet()
            filename = self.save_tweet(tweet)
            print(f"Generated tweet: {tweet['text']} → {filename}")
            time.sleep(delay)

if __name__ == "__main__":
    generator = TweetGenerator()
    # Modify this part to set the delay as needed and start generating tweets
    generator.generate_stream(delay=0.5)
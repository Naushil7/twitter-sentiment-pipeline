import json
from pathlib import Path
import os
from textblob import TextBlob
import pandas as pd
import time

class SentimentAnalyzer:
    def __init__(self, input_dir="data/raw", output_dir="data/processed"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Keep track of processed files
        self.processed_files = set()
    
    def analyze_sentiment(self, text):
        """Analyze the sentiment of text using TextBlob"""
        analysis = TextBlob(text)
        
        # Convert polarity to sentiment category
        polarity = analysis.sentiment.polarity
        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        return {
            "polarity": polarity,
            "subjectivity": analysis.sentiment.subjectivity,
            "sentiment": sentiment
        }
    
    def process_file(self, filepath):
        """Process a single tweet file"""
        with open(filepath, 'r') as f:
            tweet = json.load(f)
        
        # Add sentiment analysis
        sentiment_data = self.analyze_sentiment(tweet['text'])
        tweet.update(sentiment_data)
        
        # Save processed tweet
        output_path = f"{self.output_dir}/processed_{os.path.basename(filepath)}"
        with open(output_path, 'w') as f:
            json.dump(tweet, f)
            
        return tweet, output_path
    
    def process_directory(self):
        """Process all new files in the input directory"""
        all_files = set(os.path.join(self.input_dir, f) for f in os.listdir(self.input_dir) 
                     if f.endswith('.json'))
        new_files = all_files - self.processed_files
        
        results = []
        for filepath in new_files:
            tweet, output_path = self.process_file(filepath)
            self.processed_files.add(filepath)
            results.append(tweet)
            print(f"Processed: {tweet['text']} → {output_path}")
        
        return results
    
    def run_continuous(self, interval=2.0):
        """Run the analyzer continuously, checking for new files periodically"""
        print(f"Starting continuous processing. Checking every {interval} seconds...")
        try:
            while True:
                self.process_directory()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Stopping sentiment analysis")
    
    def generate_summary(self):
        """Generate a summary of all processed tweets"""
        processed_files = [f for f in os.listdir(self.output_dir) if f.endswith('.json')]
        
        if not processed_files:
            return "No processed tweets found."
        
        all_tweets = []
        for filename in processed_files:
            with open(os.path.join(self.output_dir, filename), 'r') as f:
                all_tweets.append(json.load(f))
        
        df = pd.DataFrame(all_tweets)
        
        summary = {
            "total_tweets": len(df),
            "sentiment_counts": df['sentiment'].value_counts().to_dict(),
            "topic_counts": df['topic'].value_counts().to_dict(),
            "avg_polarity": df['polarity'].mean(),
            "avg_subjectivity": df['subjectivity'].mean()
        }
        
        return summary

if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    analyzer.run_continuous()
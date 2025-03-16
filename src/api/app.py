from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import pandas as pd
from datetime import datetime

app = FastAPI(title="Twitter Sentiment API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to processed tweets
PROCESSED_DIR = "data/processed"

@app.get("/")
def read_root():
    return {"message": "Twitter Sentiment Analysis API"}

@app.get("/tweets")
def get_tweets(limit: int = 50, sentiment: str = None, topic: str = None):
    """Get processed tweets with optional filtering"""
    try:
        # Load all processed tweets
        tweets = []
        for filename in os.listdir(PROCESSED_DIR):
            if not filename.endswith('.json'):
                continue
                
            with open(os.path.join(PROCESSED_DIR, filename), 'r') as f:
                tweet = json.load(f)
                tweets.append(tweet)
        
        # Convert to dataframe for easier filtering
        df = pd.DataFrame(tweets)
        
        # Apply filters if provided
        if sentiment:
            df = df[df['sentiment'] == sentiment]
        
        if topic:
            df = df[df['topic'] == topic]
        
        # Sort by timestamp (newest first) and limit
        if 'created_at' in df.columns:
            df = df.sort_values('created_at', ascending=False)
        
        # Return as dictionary
        results = df.head(limit).to_dict('records')
        return {"tweets": results, "count": len(results)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary")
def get_summary():
    """Get summary statistics of processed tweets"""
    try:
        # Load all processed tweets
        tweets = []
        for filename in os.listdir(PROCESSED_DIR):
            if not filename.endswith('.json'):
                continue
                
            with open(os.path.join(PROCESSED_DIR, filename), 'r') as f:
                tweet = json.load(f)
                tweets.append(tweet)
        
        if not tweets:
            return {"message": "No tweets processed yet"}
        
        df = pd.DataFrame(tweets)
        
        summary = {
            "total_tweets": len(df),
            "sentiment_distribution": df['sentiment'].value_counts().to_dict(),
            "topic_distribution": df['topic'].value_counts().to_dict(),
            "avg_polarity": float(df['polarity'].mean()) if 'polarity' in df.columns else 0,
            "avg_subjectivity": float(df['subjectivity'].mean()) if 'subjectivity' in df.columns else 0,
            "prediction_accuracy": None  # We'll calculate this next
        }
        
        # Calculate prediction accuracy if we have ground truth
        if 'actual_sentiment' in df.columns and 'sentiment' in df.columns:
            accuracy = (df['sentiment'] == df['actual_sentiment']).mean()
            summary["prediction_accuracy"] = float(accuracy)
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
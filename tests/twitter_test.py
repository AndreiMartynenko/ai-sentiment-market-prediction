# src/tests/twitter_test.py
import tweepy
import os
import time
from dotenv import load_dotenv

# 1. Environment Setup
load_dotenv('../.env')

# 2. Client Configuration
try:
    client = tweepy.Client(
        bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        wait_on_rate_limit=True  # Essential for production
    )
except tweepy.TweepyException as e:
    print(f"Failed to initialize client: {e}")
    exit(1)

# 3. Test Query (Works for all access tiers)
TEST_QUERY = "TSLA OR Tesla -is:retweet"  # Fallback for Essential access
# TEST_QUERY = "$TSLA -is:retweet"  # Uncomment if you have Elevated/Academic access

# 4. Tweet Count Test
def test_tweet_counts():
    try:
        counts = client.get_recent_tweets_count(
            query=TEST_QUERY,
            granularity="day"
        )
        print(f"TSLA mentions last 7 days: {counts.data}")
        return True
    except tweepy.errors.BadRequest as e:
        print(f"Query syntax error: {e}")
        print("Tip: If using $ operator, ensure you have Elevated/Academic access")
        return False
    except tweepy.errors.Unauthorized as e:
        print(f"Auth error: Regenerate your Bearer Token. {e}")
        return False

# 5. Streaming Test
class SafeStream(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        try:
            print(f"New tweet: {tweet.text[:80]}...")
        except Exception as e:
            print(f"Error processing tweet: {e}")

    def on_errors(self, errors):
        print(f"Stream error: {errors}")
        time.sleep(60)  # Backoff on errors


if __name__ == "__main__":
    if test_tweet_counts():
        print("\nStarting stream... (Ctrl+C to stop)")
        stream = SafeStream(os.getenv("TWITTER_BEARER_TOKEN"))
        
        # Clear old rules
        if stream.get_rules().data:
            stream.delete_rules(stream.get_rules().data)
            
        # Add new rule
        rule = tweepy.StreamRule(TEST_QUERY)
        stream.add_rules(rule)
        
        try:
            stream.filter()
        except KeyboardInterrupt:
            print("Stream stopped by user")
        except Exception as e:
            print(f"Fatal stream error: {e}")
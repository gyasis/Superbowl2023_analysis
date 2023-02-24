import tweepy
import pandas as pd
import time
import pickle
import os
import tqdm 
from datetime import datetime, timedelta

# Define the search query and date range
query = "#superbowl OR #superbowl2023 OR #NFL OR #SBLVI place:96683cc9126741d1 -filter:retweets"

# Define the start and end times for the search
start_est = datetime(2023, 2, 12, 17, 0, 0)  # Super Bowl start time (5:00 PM EST)
start_utc = start_est - timedelta(hours=5)  # Convert to UTC
end_est = start_est + timedelta(hours=7)  # Post-game period (7 hours after start)
end_utc = end_est - timedelta(hours=5)  # Convert to UTC

# Define the maximum number of tweets to retrieve
max_tweets = 1000

# Define the filename for the pickle file and CSV file
pickle_filename = "sb_checkpoint.pickle"
csv_filename = "sb_tweets.csv"

# Define the column names for the CSV file
columns = ["id", "created_at", "text", "lang", "favorite_count", "retweet_count", "user_location"]

# Create an empty DataFrame to store the tweets
if pickle_filename in os.listdir():
    # Load the DataFrame and max_id from the pickle file
    with open(pickle_filename, "rb") as f:
        df, max_id = pickle.load(f)
else:
    # Create a new DataFrame if the pickle file doesn't exist
    df = pd.DataFrame(columns=columns)
    max_id = None

# Authenticate with the Twitter API

consumer_key = 'amKQslbHGOqwXgX6O5PaBXL75'
consumer_secret = 'q9TrxNYiNuBH9euEwq1KXaNas5tPpypHLrY1yeNobo9ECiHlVV'
access_token = '10205062-kNfkISitiPHU25iov2d9hSxwnnl1RPcZRgVb8uemU'
access_token_secret = 'HgLDdqQjTk9HMs9BKyAf1gGdeCCXZs1T6oVBLlC74gTu3'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Create the Tweepy API object
api = tweepy.API(auth)

# Loop over requests until we reach the maximum number of tweets
request_count = 0
while len(df) < max_tweets:
    # Check the rate limit status before making a request
    rate_limit_status = api.rate_limit_status()
    remaining_requests = rate_limit_status["resources"]["search"]["/search/tweets"]["remaining"]
    reset_time = rate_limit_status["resources"]["search"]["/search/tweets"]["reset"]
    now = time.time()
    
    if remaining_requests <= 150 and reset_time > now:
        # Sleep for 16 minutes if the remaining requests are less than or equal to 150
        sleep_time = 16 * 60
        print(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time)

    if remaining_requests == 0 and reset_time > now:
        # Sleep until the rate limit resets
        sleep_time = reset_time - now + 5
        print(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time)
        
    # Get the maximum ID of the currently retrieved tweets
    max_id = df["id"].max() if not df.empty else None
    
    # Search for tweets containing the hashtag and within the specified date range
    tweets = tweepy.Cursor(api.search_tweets, q=query, count=100, lang="en", max_id=max_id, since_id=start_utc, until=end_utc).items()
    
    # Loop over tweets and add them to the DataFrame
    for i, tweet in tqdm.tqdm(enumerate(tweets)):
        # Extract the relevant information from the tweet
        tweet_data = {
            "id": tweet.id_str,
            "created_at": tweet.created_at,
            "text": tweet.full_text,
            "lang": tweet.lang,
            "favorite_count": tweet.favorite_count,
            "retweet_count": tweet.retweet_count,
            "user_location": tweet.user.location,
        }
        
        # Add the tweet to the DataFrame
        df = df.append(tweet_data, ignore_index=True)
        
        # Update the maximum ID of the retrieved tweets
        max_id = tweets[-1].id - 1
        
        # Print the progress
        print(f"Retrieved {len(df)} tweets.")
        
        # Check if we have reached the maximum number of tweets
        if len(df) >= max_tweets:
            break
    
    with open(pickle_filename, "wb") as f:
        pickle.dump((df, max_id), f)
    
    # Save the DataFrame to a CSV file
    df.to_csv(csv_filename, index=False)
    print(f"Saved {len(df)} tweets to {csv_filename}.")
    print(f"The last 5 tweets are:", df.tail(5), sep="\n")
    
    # Check if we have reached the maximum number of tweets
    print(len(df))
    if len(df) >= max_tweets:
        break
    
    # Increment the request count
    request_count += 1
    
    # Print the request count
    print(f"Completed request {request_count}.")
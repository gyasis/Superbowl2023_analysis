# %%

import tweepy
import re
import pandas as pd
from textblob import TextBlob
from time import sleep
from tqdm import tqdm

# Connect to the Twitter API
consumer_key = 'amKQslbHGOqwXgX6O5PaBXL75'
consumer_secret = 'q9TrxNYiNuBH9euEwq1KXaNas5tPpypHLrY1yeNobo9ECiHlVV'
access_token = '10205062-kNfkISitiPHU25iov2d9hSxwnnl1RPcZRgVb8uemU'
access_token_secret = 'HgLDdqQjTk9HMs9BKyAf1gGdeCCXZs1T6oVBLlC74gTu3'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, 
                #  wait_on_rate_limit=True
                 )

# Define keywords to search for
# keywords = ['superbowl', 'referee', 'halftime', 'commercials']
keywords =  ['superbowl']
# Define entities to extract using NLP techniques
entities = ['PERSON']

# Define the maximum number of requests and the time period for rate limiting
max_requests = 5
request_interval = 15 * 60 / max_requests

# Define the filename for the CSV file
filename = 'superbowl_tweets.csv'

# Define the resume data filename
resume_filename = 'resume_data.pkl'

# Initialize the resume data dictionary
resume_data = {'max_id': None, 'df': pd.DataFrame()}

try:
    # Check if there is existing resume data and load it
    resume_data = pd.read_pickle(resume_filename)
    print('Resume data loaded successfully.')
except FileNotFoundError:
    print('No resume data found.')
# %%
# Fetch tweets containing the keywords and entities
tweets = resume_data['df']
requests = 0
for keyword in keywords:
    search_query = keyword + ' -filter:retweets'
    max_id = resume_data['max_id']
    for tweet in tqdm(tweepy.Cursor(api.search_tweets, q=search_query, lang='en', tweet_mode='extended', max_id=max_id).items(), desc=f'{keyword} tweets'):
        full_text = tweet.full_text
        # Remove URLs and mentions
        full_text = re.sub(r'http\S+', '', full_text)
        full_text = re.sub(r'@\S+', '', full_text)
        # Extract entities
        blob = TextBlob(full_text)
        for sentence in blob.sentences:
            for word, tag in sentence.tags:
                if tag in entities:
                    tweets = tweets.append({'text': full_text, 'entity': word, 'keyword': keyword}, ignore_index=True)

        # Update the max_id to avoid retrieving duplicates
        max_id = tweet.id

        # Save the current max_id and DataFrame to the resume data dictionary
        resume_data['max_id'] = max_id
        resume_data['df'] = tweets

        # Rate limiting logic
        requests += 1
        if requests >= max_requests:
            requests = 0
            sleep(request_interval)

        # Save the resume data to a file
        pd.to_pickle(resume_data, resume_filename)

    try:
        # Check if there is existing resume data and load it
        resume_data = pd.read_pickle(resume_filename)
        print('Resume data loaded successfully.')
    except FileNotFoundError:
        print('No resume data found.')

    except tweepy.RateLimitError:
        print('Rate limit exceeded. Sleeping for 15 minutes...')
        sleep(15 * 60)

    except Exception as e:
        print(f'Error occurred: {str(e)}')
        break

# Save the tweets to a Pandas DataFrame
df = pd.DataFrame(tweets)

# Save the DataFrame to a CSV file
df.to_csv(filename, index=False)
# %%

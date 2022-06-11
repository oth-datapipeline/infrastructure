"""Generic batch script for data migration on all three data sources
If the field sentiment doesn't exist, add a sentiment analysis of the field text to the article, post or tweet.
! The same script can be used for all three data sources, as only line 11 to 13 changes !
"""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from utils import read_args, get_database

if __name__ == '__main__':
    remote = read_args(__file__)
    database = get_database(remote)
    # collection = database['rss.articles']
    # collection = database['reddit.posts']
    collection = database['twitter.tweets']

    # Set up sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    tweets = collection.aggregate([
        {
            '$match': {
                'sentiment': {
                    '$exists': False
                }
            }
        }, {
            '$project': {
                'text': 1
            }
        }, {
            '$limit': 10
        }
    ])

    count = 0
    for tweet in tweets:
        scores = analyzer.polarity_scores(tweet.text)
        sentiment = {
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'positive': scores['pos'],
            'compound': scores['compound']
        }
        ret = collection.update_one({'_id': tweet['_id']}, {'$set': {'sentiment': sentiment}})
        if ret.modified_count != 1:
            print('Error in modification of data in database occurred')
            break
        count += 1
        if count in [1, 10] or count % 100 == 0:
            print(f'{count} document(s) sucessfully modified')
    
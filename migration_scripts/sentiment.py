"""Generic batch script for data migration on all three data sources
If the field sentiment doesn't exist, add a sentiment analysis of the field text to the article, post or tweet.
"""
import argparse
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from utils import get_database

def get_arguments():
    """Get script arguments from the argument parser
    """
    parser = argparse.ArgumentParser(
        description='Script for data migration on sentiment analysis')
    parser.add_argument('--remote', action='store_true', default=False, help='Data migration on remote database (default: local)')
    parser.add_argument('--limit', type=int, default=10, help='Limit on modifying entries (default: 10)')
    subparsers = parser.add_subparsers(dest='data_source', required=True)
    subparsers.add_parser('rss', help='Reload sentiment analysis on data from RSS feeds')
    subparsers.add_parser('reddit', help='Reload sentiment analysis on data from reddit')
    subparsers.add_parser('twitter', help='Reload sentiment analysis on data from twitter')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_arguments()
    print('args:', args)

    database = get_database(args.remote)
    
    if args.data_source == 'rss':
        collection_name = 'rss.articles'
    if args.data_source == 'reddit':
        collection_name = 'reddit.posts'
    if args.data_source == 'reddit':
        collection_name = 'twitter.tweets'

    collection = database[collection_name]

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
            '$limit': args.limit
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
    
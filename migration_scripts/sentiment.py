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
    reddit = subparsers.add_parser('reddit', help='Reload sentiment analysis on data from reddit')
    reddit.add_argument('--comments', action='store_true', default=False, help='Additionally add sentiment to comments (default: False)')
    subparsers.add_parser('twitter', help='Reload sentiment analysis on data from twitter')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_arguments()
    print('args:', args)

    database = get_database(args.remote)
    
    if args.data_source == 'rss':
        collection_name = 'rss.articles'
        fieldname_to_be_analyzed = 'title'
    if args.data_source == 'reddit':
        collection_name = 'reddit.posts'
        fieldname_to_be_analyzed = 'title'
    if args.data_source == 'twitter':
        collection_name = 'twitter.tweets'
        fieldname_to_be_analyzed = 'text'

    collection = database[collection_name]

    # Set up sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    results = collection.aggregate([
        {
            '$match': {
                'sentiment': {
                    '$exists': False
                }
            }
        }, {
            '$project': {
                fieldname_to_be_analyzed: 1
            }
        }, {
            '$limit': args.limit
        }
    ])

    count = 0
    for result in results:
        scores = analyzer.polarity_scores(result[fieldname_to_be_analyzed])
        sentiment = {
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'positive': scores['pos'],
            'compound': scores['compound']
        }
        ret = collection.update_one({'_id': result['_id']}, {'$set': {'sentiment': sentiment}})
        if ret.modified_count != 1:
            print('Error in modification of data in database occurred')
            break
        count += 1
        if count in [1, 10] or count % 100 == 0:
            print(f'{count} document(s) successfully modified')

    if args.data_source == 'reddit' and args.comments:
        # Adding sentiment analysis to reddit comments
        comments = collection.aggregate([
            {
                '$unwind': {
                    'path': '$comments', 
                    'includeArrayIndex': 'index'
                }
            }, {
                '$match': {
                    'comments.sentiment': {
                        '$exists': False
                    }
                }
            }, {
                '$project': {
                    'comments.text': 1, 
                    'index': 1
                }
            }, {
                '$limit': args.limit
            }
        ])

        for comment in comments:
            scores = analyzer.polarity_scores(comment['comments']['text'])
            sentiment = {
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'positive': scores['pos'],
                'compound': scores['compound']
            }
            ret = collection.update_one({'_id': result['_id']}, {'$set': {f'comments.{comment["index"]}.sentiment': sentiment}})
            if ret.modified_count != 1:
                print('Error in modification of data in database occurred')
                break
            count += 1
            if count in [1, 10] or count % 100 == 0:
                print(f'{count} document(s) successfully modified')

    print(f'Result: {count} document(s) successfully modified')
    
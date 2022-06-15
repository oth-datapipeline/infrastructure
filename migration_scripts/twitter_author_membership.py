"""Batch script for data migration on data source Twitter
If the field author.created_at doesn't exist, fetch the information via the Tweepy API, calculate
the field member_since based on author.created_at and the field created_at for the tweet, and add
both fields to the author subdocument
"""
import tweepy
from utils import read_args, get_database
from constants import TWITTER_BEARER_TOKEN

if __name__ == '__main__':
    args = read_args()
    database = get_database(args.remote)
    collection = database['twitter.tweets']

    # Set up tweepy client
    api = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

    tweets = collection.aggregate([
        {
            '$match': {
                'author.created_at': {
                    '$exists': False
                }
            }
        }, {
            '$project': {
                'author.username': 1,
                'created_at': 1
            }
        }, {
            '$limit': args.limit
        }
    ])

    count = 0
    for tweet in tweets:
        user_fields = ['created_at']
        user = api.get_user(username=tweet['author']['username'], user_fields=user_fields)
        author_created = user.data.created_at
        member_since = (tweet['created_at'] - author_created.replace(tzinfo=None)).total_seconds()
        ret = collection.update_one({'_id': tweet['_id']}, {'$set': {'author.created_at': author_created, 'author.member_since': member_since}})
        if ret.modified_count != 1:
            print('Error in modification of data in database occurred')
            break
        count += 1
        if count in [1, 10] or count % 100 == 0:
            print(f'{count} document(s) sucessfully modified')

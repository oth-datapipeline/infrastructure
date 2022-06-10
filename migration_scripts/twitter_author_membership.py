"""Batch script for data migration on data source Twitter
If the field author.created_at doesn't exist, fetch the information via the Tweepy API, calculate
the field member_since based on author.created and insert_date / comment.created and add both
fields to the author subdocument
"""
import tweepy
from utils import read_args, get_database
from constants import TWITTER_BEARER_TOKEN

if __name__ == '__main__':
    remote = read_args(__file__)
    database = get_database(remote)
    collection = database['twitter.tweets']

    # Set up PRAW API client
    api = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

    results = collection.aggregate([
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
            '$limit': 10
        }
    ])

    count = 0
    for result in results:
        user_fields = ['created_at']
        user = api.get_user(username=result['author']['username'], user_fields=user_fields)
        author_created = user.data.created_at
        member_since = (result['created_at'] - author_created.replace(tzinfo=None)).total_seconds()
        ret = collection.update_one({'_id': result['_id']}, {'$set': {'author.created_at': author_created, 'author.member_since': member_since}})
        if ret.modified_count != 1:
            print('Error in modification of data in database occurred')
            break
        count += 1
        if count in [1, 10] or count % 100 == 0:
            print(f'{count} document(s) sucessfully modified')

"""Batch script for data migration on data source Twitter
If the field author.created_at doesn't exist, fetch the information via the Tweepy API, calculate
the field member_since based on author.created and insert_date / comment.created and add both
fields to the author subdocument
"""
import sys
import tweepy
from pymongo import MongoClient
from constants import MONGODB_HOST, MONGODB_PORT, MONGODB_USERNAME, MONGODB_PASSWORD, \
                      TWITTER_BEARER_TOKEN

if __name__ == '__main__':
    if len(sys.argv) not in [1, 2] or \
        ( len(sys.argv) == 2 and sys.argv[1] != '--remote' ):
        print('Usage of script: ./twitter_author_membership.py [--remote]')

    # Set up PRAW API client
    api = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
    
    remote = False
    if len(sys.argv) == 2:
        remote = True

    if remote:
        client = MongoClient(MONGODB_HOST, MONGODB_PORT, username=MONGODB_USERNAME, password=MONGODB_PASSWORD)
    else:
        client = MongoClient('localhost', MONGODB_PORT)
    
    database = client['data']
    collection = database['twitter.tweets']

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

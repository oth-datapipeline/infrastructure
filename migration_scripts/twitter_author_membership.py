"""Batch script for data migration on data source Twitter
If the field author.created_at doesn't exist, fetch the information via the Tweepy API, calculate
the field member_since based on author.created_at and the field created_at for the tweet, and add
both fields to the author subdocument
"""
import tweepy
import sys
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

    usernames_dict = {}
    for tweet in tweets:
        if tweet['author']['username'] in usernames_dict:
            usernames_dict[tweet['author']['username']].append((tweet['_id'], tweet['created_at']))
        else:
            usernames_dict[tweet['author']['username']] = [(tweet['_id'], tweet['created_at'])]

    usernames_list = [list(usernames_dict.keys())[i:i + 100] for i in range(0, len(usernames_dict), 100)]

    count = 0
    for usernames in usernames_list:
        user_fields = ['created_at']
        response = api.get_users(usernames=usernames, user_fields=user_fields)
        if len(response.errors) > 0:
            print('Error: ', response.errors[0]['detail'])
        if response.data:
            for user in response.data:
                if user.username not in usernames_dict:
                    print(f'Warning: The username {user.username} is not in the dictionary')
                    continue
                for tweet_id, tweet_created_at in usernames_dict[user.username]:
                    author_created = user.created_at
                    member_since = (tweet_created_at - author_created.replace(tzinfo=None)).total_seconds()
                    ret = collection.update_one({'_id': tweet_id}, {'$set': {'author.created_at': author_created, 'author.member_since': member_since}})
                    if ret.modified_count != 1:
                        print('Error in modification of data in database occurred')
                        print(f'Result: {count} document(s) sucessfully modified')
                        sys.exit(0)
                    count += 1
                    if count in [1, 10] or count % 100 == 0:
                        print(f'{count} document(s) sucessfully modified')

    print(f'Result: {count} document(s) sucessfully modified')

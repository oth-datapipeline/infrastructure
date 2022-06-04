"""Batch script for data migration on data source Reddit
If the field author.created is -1 (this can be the author of the post itself, but also the author
of a comment), fetch the information via the PRAW API and recalculate the field member_since based
on author.created and insert_date / comment.created
"""
import datetime
import sys
import praw
from pymongo import MongoClient
from constants import MONGODB_HOST, MONGODB_PORT, MONGODB_USERNAME, MONGODB_PASSWORD, \
                      REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

if __name__ == '__main__':
    if len(sys.argv) not in [1, 2] or \
        ( len(sys.argv) == 2 and sys.argv[1] != '--remote' ):
        print('Usage of script: ./reddit_member_since.py [--remote]')

    # Set up PRAW API client
    api = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)
    
    remote = False
    if len(sys.argv) == 2:
        remote = True

    if remote:
        client = MongoClient(MONGODB_HOST, MONGODB_PORT, username=MONGODB_USERNAME, password=MONGODB_PASSWORD)
    else:
        client = MongoClient('localhost', MONGODB_PORT)
    
    database = client['data']
    collection = database['reddit.posts']

    authors = collection.aggregate([
        {
            '$match': {
                'author.created': -1
            }
        }, {
            '$group': {
                '_id': '$author.name'
            }
        }, {
            '$limit': 10
        }
    ])

    comment_authors = collection.aggregate([
        {
            '$unwind': {
                'path': '$comments'
            }
        }, {
            '$match': {
                'comments.author.created': -1
            }
        }, {
            '$group': {
                '_id': '$comments.author.name'
            }
        }, {
            '$limit': 10
        }
    ])

    all_authors = set()
    for author in authors:
        all_authors.add(author['_id'])
    for author in comment_authors:
        all_authors.add(author['_id'])

    count = 0
    for author_name in all_authors:
        print(f'Fetching the creation date of redditor {author_name}')
        redditor = api.redditor(name=author_name)
        try:
            author_created = datetime.datetime.fromtimestamp(redditor.created)
        except AttributeError:
            print(f'The field created for the redditor {author_name} can\'t be fetched from the PRAW API')
            continue

        # Modifying the creation date of the author of a post
        results = collection.aggregate([
            {
                '$match': {
                    'author.name': author_name, 
                    'author.created': -1
                }
            }, {
                '$project': {
                    'created': 1
                }
            }, {
                '$limit': 100
            }
        ])

        for result in results:
            member_since = (result['created'] - author_created).total_seconds()
            ret = collection.update_one({'_id': result['_id']}, {'$set': {'author.created': author_created, 'author.member_since': member_since}})
            if ret.modified_count != 1:
                print('Error in modification of data in database occurred')
                break
            count += 1
            if count in [1, 10] or count % 100 == 0:
                print(f'{count} document(s) sucessfully modified')

        # Modifying the creation date of the author of a comment
        results = collection.aggregate([
            {
                '$unwind': {
                    'path': '$comments', 
                    'includeArrayIndex': 'index'
                }
            }, {
                '$match': {
                    'comments.author.name': author_name, 
                    'comments.author.created': -1
                }
            }, {
                '$project': {
                    'index': 1, 
                    'comments.created': 1
                }
            }, {
                '$limit': 100
            }
        ])

        for result in results:
            member_since = (result['comments.created'] - author_created).total_seconds()
            ret = collection.update_one({'_id': result['_id']}, {'$set': {f'comments.{result["index"]}.author.created': author_created, f'comments.{result["index"]}.author.member_since': member_since}})
            if ret.modified_count != 1:
                print('Error in modification of data in database occurred')
                break
            count += 1
            if count in [1, 10] or count % 100 == 0:
                print(f'{count} document(s) sucessfully modified')

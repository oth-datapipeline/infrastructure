"""Batch script for data migration on data source Reddit
If the field author.created is -1 (this can be the author of the post itself, but also the author
of a comment), fetch the information via the PRAW API and recalculate the field member_since based
on author.created and insert_date / comment.created
"""
import datetime
import praw
from utils import read_args, get_database
from constants import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

if __name__ == '__main__':
    args = read_args()
    database = get_database(args.remote)
    collection = database['reddit.posts']

    # Set up PRAW API client
    api = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)

    post_authors = collection.aggregate([
        {
            '$match': {
                'author.created': -1
            }
        }, {
            '$group': {
                '_id': '$author.name'
            }
        }, {
            '$limit': args.limit
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
            '$limit': args.limit
        }
    ])

    all_authors = set()
    for author in post_authors:
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
        posts = collection.aggregate([
            {
                '$match': {
                    'author.name': author_name, 
                    'author.created': -1
                }
            }, {
                '$project': {
                    'created': 1
                }
            }
        ])

        for post in posts:
            member_since = (post['created'] - author_created).total_seconds()
            ret = collection.update_one({'_id': post['_id']}, {'$set': {'author.created': author_created, 'author.member_since': member_since}})
            if ret.modified_count != 1:
                print('Error in modification of data in database occurred')
                break
            count += 1
            if count in [1, 10] or count % 100 == 0:
                print(f'{count} document(s) sucessfully modified')

        # Modifying the creation date of the author of a comment
        posts_with_comment_index = collection.aggregate([
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
            }
        ])

        for post_with_comment_index in posts_with_comment_index:
            member_since = (post_with_comment_index['comments.created'] - author_created).total_seconds()
            ret = collection.update_one({'_id': post_with_comment_index['_id']},
                {'$set': {f'comments.{post_with_comment_index["index"]}.author.created': author_created, f'comments.{post_with_comment_index["index"]}.author.member_since': member_since}})
            if ret.modified_count != 1:
                print('Error in modification of data in database occurred')
                break
            count += 1
            if count in [1, 10] or count % 100 == 0:
                print(f'{count} document(s) sucessfully modified')

    print(f'Result: {count} document(s) sucessfully modified')

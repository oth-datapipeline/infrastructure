"""Batch script for data migration on data source RSS Feeds
If the field published is of type String, then cast it to type ISODate (datetime.datetime)
to standardize the data
"""
import datetime
import sys
from pymongo import MongoClient
from constants import MONGODB_HOST, MONGODB_PORT, MONGODB_USERNAME, MONGODB_PASSWORD

if __name__ == '__main__':
    if len(sys.argv) not in [1, 2] or \
        ( len(sys.argv) == 2 and sys.argv[1] != '--remote' ):
        print('Usage of script: ./rss_published_string.py [--remote]')
    
    remote = False
    if len(sys.argv) == 2:
        remote = True

    if remote:
        client = MongoClient(MONGODB_HOST, MONGODB_PORT, username=MONGODB_USERNAME, password=MONGODB_PASSWORD)
    else:
        client = MongoClient('localhost', MONGODB_PORT)
    
    database = client['data']
    collection = database['rss.articles']

    results = collection.aggregate([
        {
            '$project': {
                'published': 1,
                'type_published': {
                    '$type': '$published'
                }
            }
        }, {
            '$match': {
                'type_published': 'string'
            }
        }, {
            '$project': {
                'published': 1
            }
        }, {
            '$limit': 100
        }
    ])

    count = 0
    for result in results:
        timezone_string = result['published'].split(" ")[-1]
        timezone_char = "%z" if any(c.isdigit() for c in timezone_string) else "%Z"
        published_date = datetime.datetime.strptime(result['published'], f"%a, %d %b %Y %H:%M:%S {timezone_char}")
        ret = collection.update_one({'_id': result['_id']}, {'$set': {'published': published_date}})
        if ret.modified_count != 1:
            print('Error in modification of data in database occurred')
            break
        count += 1
        if count in [1, 10] or count % 100 == 0:
            print(f'{count} document(s) sucessfully modified')

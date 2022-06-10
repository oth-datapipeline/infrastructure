"""Batch script for data migration on data source RSS Feeds
If the field published is of type String, then cast it to type ISODate (datetime.datetime)
to standardize the data
"""
import datetime
from utils import read_args, get_database

if __name__ == '__main__':
    remote = read_args(__file__)
    database = get_database(remote)
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

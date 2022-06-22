"""Batch script for data migration on data source RSS Feeds
If the field published is of type String, then cast it to type ISODate (datetime.datetime)
to standardize the data
"""
import datetime
import pytz
from utils import read_args, get_database

tzinfos = {}
for tz in map(pytz.timezone, pytz.all_timezones):
    for _, _, tzname in getattr(tz, '_transition_info', []):
        if not any(c.isdigit() for c in tzname):
            tzinfos[tzname] = tz

if __name__ == '__main__':
    args = read_args()
    database = get_database(args.remote)
    collection = database['rss.articles']

    articles = collection.aggregate([
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
            '$limit': args.limit
        }
    ])

    count = 0
    for article in articles:
        """There's a known issue here: datetime.strptime can only parse datetimes with a local timestamp or UTC or GMT.
        This issue is documented here: https://bugs.python.org/issue22377
        Workaround by manually localizing the datetimes with dict tzinfos
        """
        if article['published'] == '':
            print('Warning: published_date is empty string')
            continue

        timezone_string = article['published'].rpartition(' ')[2]
        if len(timezone_string) == 25: # Handle special case No. 1
            published_date = datetime.datetime.strptime(article['published'], '%Y-%m-%dT%H:%M:%S%z')
        elif len(timezone_string) == 20: # Handle special case No. 2
            published_date = datetime.datetime.strptime(article['published'], '%Y-%m-%dT%H:%M:%SZ')
        elif len(timezone_string) == 29: # Handle special case No. 3
            published_date = datetime.datetime.strptime(article['published'], '%Y-%m-%dT%H:%M:%S.%f%z')
        elif any(c.isdigit() for c in timezone_string):
            published_date = datetime.datetime.strptime(article['published'], '%a, %d %b %Y %H:%M:%S %z')
        elif timezone_string in tzinfos:
            naive_date = datetime.datetime.strptime(article['published'].rpartition(' ')[0], '%a, %d %b %Y %H:%M:%S')
            published_date = tzinfos[timezone_string].localize(naive_date)
        else:
            published_date = datetime.datetime.strptime(article['published'].rpartition(' ')[0], '%a, %d %b %Y %H:%M:%S')

        ret = collection.update_one({'_id': article['_id']}, {'$set': {'published': published_date}})
        if ret.modified_count != 1:
            print('Error in modification of data in database occurred')
            break
        
        count += 1
        if count in [1, 10] or count % 100 == 0:
            print(f'{count} document(s) successfully modified')

    print(f'Result: {count} document(s) successfully modified')

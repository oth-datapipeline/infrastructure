"""Batch script for data migration on data source Twitter
If the field place exists, the Twitter user chose to publish its location data.
Use geopy to fetch longitude and latitude values for each place.
"""
import argparse
import sys
from utils import read_args, get_database
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_arguments():
    """Get script arguments from the argument parser
    """
    parser = argparse.ArgumentParser(
        description='Script for fetching tweet geo data via geopy.')
    parser.add_argument('--remote', action='store_true', default=False, help='Data migration on remote database (default: local)')
    parser.add_argument('--limit', type=int, default=10, help='Limit on modifying entries (default: 10)')
    return parser.parse_args()

def get_geodata(geolocator, address, attempt=1, max_attempts=5):
    try:
        return geolocator.geocode(address)
    except GeocoderTimedOut:
        if attempt <= max_attempts:
            return get_geodata(geolocator, address, attempt=attempt+1)
        raise

if __name__ == '__main__':
    args = get_arguments()
    database = get_database(args.remote)
    collection = database['twitter.tweets']

    # Setup geopy
    # Initialize Nominatim API
    geolocator = Nominatim(user_agent="linux:oth.datapipeline:v0.1", timeout=1)

    tweets = collection.aggregate([
        {
            '$match': {
                'place': {
                    '$exists': True,
                    '$ne': None
                },
                'geo': {
                    '$exists': False
                }
            }
        }, {
            '$project': {
                'place': '$place'
            }
        }, {
            '$limit': args.limit
        }
    ])

    count = 0

    for tweet in tweets:
        location = get_geodata(geolocator, tweet["place"])
        if location is not None:
            geo = {
                    'lat': location.latitude,
                    'long': location.longitude
                }
            
            ret = collection.update_one(
                {'_id': tweet["_id"]},
                {'$set': {'geo': geo, }
            })

            if ret.modified_count != 1:
                print('Error in modification of data in database occurred')
                print(
                    f'Result: {count} document(s) successfully modified')
                sys.exit(0)

            count += 1
            if count in [1, 10] or count % 100 == 0:
                print(f'{count} document(s) successfully modified')
        else:
            print(f'Could not fetch geo data for place \'{tweet["place"]}\' of tweet {tweet["_id"]}.')
            continue

    print(f'Result: {count} document(s) successfully modified')

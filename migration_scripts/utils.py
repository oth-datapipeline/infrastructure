import argparse
import pymongo
from constants import MONGODB_HOST, MONGODB_PORT, MONGODB_USERNAME, MONGODB_PASSWORD

def read_args() -> argparse.Namespace:
    """Get script arguments from the argument parser
    """
    parser = argparse.ArgumentParser(description='Script for data migration')
    parser.add_argument('--remote', action='store_true', default=False, help='Data migration on remote database (default: local)')
    parser.add_argument('--limit', type=int, default=10, help='Limit on modifying entries (default: 10)')
    return parser.parse_args()

def get_database(remote : bool = False) -> pymongo.database.Database:
    if remote:
        client = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT, username=MONGODB_USERNAME, password=MONGODB_PASSWORD)
    else:
        client = pymongo.MongoClient('localhost', MONGODB_PORT, username=MONGODB_USERNAME, password=MONGODB_PASSWORD)
    
    database = client['data']
    print('Connecting to database:', database)
    return database
import sys
import pymongo
from constants import MONGODB_HOST, MONGODB_PORT, MONGODB_USERNAME, MONGODB_PASSWORD

def read_args(filename : str) -> bool:
    if len(sys.argv) not in [1, 2] or \
        ( len(sys.argv) == 2 and sys.argv[1] != '--remote' ):
        print(f'Usage of script: ./{filename} [--remote]')
        sys.exit(-1)

    remote = False
    if len(sys.argv) == 2:
        remote = True

    return remote

def get_database(remote : bool = False) -> pymongo.database.Database:
    if remote:
        client = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT, username=MONGODB_USERNAME, password=MONGODB_PASSWORD)
    else:
        client = pymongo.MongoClient('localhost', MONGODB_PORT)
    
    database = client['data']
    print(database)
    print(type(database))
    return database
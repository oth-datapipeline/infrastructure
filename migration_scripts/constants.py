import os
from dotenv import load_dotenv

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docker-compose', '.env'))
load_dotenv(dotenv_path=dotenv_path)

# Constants for environment variables
REDDIT_CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
REDDIT_CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']
REDDIT_USER_AGENT = 'linux:oth.datapipeline:v0.1'
TWITTER_CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
TWITTER_CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
TWITTER_BEARER_TOKEN = os.environ['TWITTER_BEARER_TOKEN']
MONGODB_HOST = os.environ['MONGO_HOST']
MONGODB_PORT = 27017
MONGODB_USERNAME = os.environ['MONGO_INITDB_ROOT_USERNAME']
MONGODB_PASSWORD = os.environ['MONGO_INITDB_ROOT_PASSWORD']

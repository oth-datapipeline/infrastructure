# Data migration, formatting, reloading, ...

This folder contains a collection of various python scripts, which don't depend from each other. They all can be runned on their own without interfering with the remaining data pipeline. The migration scripts are not part of the data pipeline, but mitigate the data on the MongoDB database server post hoc.  

For help to run the scripts, please use the commandline help functionality `-h` / `--help`.

Note that all scripts support local debugging by default. To run the scripts on the remote database, additionally use the commandline argument `--remote`. To scale up the limit of to-be-modified data entries, additionally use the commandline argument `--limit INTEGER`.

List of scripts:  
- Adding the `created` and `member_since` field for the author of a reddit post or comment ([reddit_author_membership.py](reddit_author_membership.py))
- Adding the `created_at` and `member_since` field for the author of a twitter tweet ([twitter_author_membership.py](twitter_author_membership.py))
- Modify the data format for the field `published` in an RSS feed from string to ISODate ([rss_published_string.py](rss_published_string.py))
- Adding post hoc sentiment analysis to articles, posts, comments and tweets ([sentiment.py](sentiment.py))
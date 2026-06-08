import datetime
import json

import pymongo
import tweepy

import config


TRACK_TERMS = ["#oscars"]


def create_api():
    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_key, config.access_secret)
    return tweepy.API(auth)


class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, api, mongo_client=None):
        self.api = api
        super(CustomStreamListener, self).__init__()
        client = mongo_client or pymongo.MongoClient(config.mongo_url)
        self.db = client.TweetDB

    def on_data(self, tweet):
        try:
            data = json.loads(tweet)
        except ValueError:
            return True
        if not isinstance(data, dict):
            return True

        user = data.get("user") or {}
        if not isinstance(user, dict):
            return True
        text = data.get("text")
        screen_name = user.get("screen_name")
        if not text or not screen_name:
            return True

        self.db.tweets.insert({
            "text": text,
            "date": datetime.datetime.now(datetime.timezone.utc),
            "screen_name": screen_name,
        })
        return True

    def on_error(self, status_code):
        return True  # Don't kill the stream

    def on_timeout(self):
        return True  # Don't kill the stream


def create_stream(api):
    return tweepy.streaming.Stream(api.auth, CustomStreamListener(api))


def start_stream(track_terms=None):
    api = create_api()
    streaming_api = create_stream(api)
    streaming_api.filter(track=track_terms or TRACK_TERMS)
    return streaming_api


if __name__ == "__main__":
    start_stream()

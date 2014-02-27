import json
import pymongo
import tweepy
import datetime
import os
import config

auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_key, config.access_secret)
api = tweepy.API(auth)


class CustomStreamListener(tweepy.StreamListener):
	def __init__(self, api):
		self.api = api
		super(tweepy.StreamListener, self).__init__()
		# TweetDB is the name of the DB
		self.db = pymongo.MongoClient(config.mongo_url).TweetDB

	def on_data(self, tweet):
		# contains the full tweet
		data = json.loads(tweet)
		text = data['text']
		screen_name = data['user']['screen_name']
		date = datetime.datetime.utcnow()
		# just pushing a few things into the DB
		self.db.tweets.insert({"text": text, "date": date, "screen_name": screen_name})

	def on_error(self, status_code):
		return True # Don't kill the stream

	def on_timeout(self):
		return True # Don't kill the stream


# create stream
streaming_api = tweepy.streaming.Stream(auth, CustomStreamListener(api))
# filter for the oscars
straming_api.filter(track=['#oscars'])
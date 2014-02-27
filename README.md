Sample application with HEROKU for streaming data to MongoHQ.

heroku create
heroku addons:add mongohq:free
heroku config:add consumer_key=consumer_key
heroku config:add consumer_secret=consumer_secret
heroku config:add access_key=access_key
heroku config:add access_secret=access_secret


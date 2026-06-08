import os


def required_env(*names):
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    raise RuntimeError("Missing required environment variable: " + " or ".join(names))


consumer_key = required_env("consumer_key", "CONSUMER_KEY")
consumer_secret = required_env("consumer_secret", "CONSUMER_SECRET")
access_key = required_env("access_key", "ACCESS_KEY")
access_secret = required_env("access_secret", "ACCESS_SECRET")
mongo_url = required_env("MONGOHQ_URL", "MONGO_URL")

import os


def required_env(*names):
    for name in names:
        value = os.environ.get(name)
        if value:
            value = value.strip()
        if value:
            return value
    raise RuntimeError("Missing required environment variable: " + " or ".join(names))


def bearer_token():
    return required_env("bearer_token", "BEARER_TOKEN")


def mongo_url():
    return required_env("MONGOHQ_URL", "MONGO_URL")

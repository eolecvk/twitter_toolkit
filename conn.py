_twitter_api = None

def get_twitter_api():
    global _twitter_api
    if not _twitter_api:
        from credentials import app_key, app_secret
        from twython import Twython, TwythonError
        twitter = Twython(app_key=app_key, app_secret=app_secret, oauth_version=2)
        access_token = twitter.obtain_access_token() # Store `access_token`(?)
        twitter_api = Twython(app_key=app_key, access_token=access_token)
    return twitter_api
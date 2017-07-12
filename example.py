
import twitter_mining

def preprocess_screen_name(screen_name):
    """
    Removes preceeding '@' in Twitter user handle if applicable
    Returns lowercase screen_name
    """
    try:
        if screen_name[0] == '@':
            screen_name.pop(0)
        screen_name = screen_name.lower()
        return screen_name
    except:
        return ''


def get_tweets_for_users(twitter_api, users_screen_name=[]):
    """
    1. Get the twitter user ids for the users in `users_screen_name`
    2. For each existing and public user in the user ids list, get the user timeline
    3. Return user timelines as dict, { user_id : [{tweets}], ...}

    Keyword args:
    `users_screen_name` list of twitter user handle (eg: potus, kanye_west,..)

    """
    user_timeline_dict = {}

    for screen_name in users_screen_name:
        screen_name_clean = preprocess_screen_name(screen_name)
        user_timeline = twitter_mining.get_user_timeline(
            twitter_api=twitter_api,
            screen_name=screen_name_clean, user_id=None)

        if user_timeline:
            user_timeline_dict[screen_name_clean] = user_timeline
            # Here you might wanna save directly to a DB instead!

    return user_timeline_dict



if __name__ == "__main__":

    # Get list of input users
    input_users = [
        'TheNstitute',
        'BlackHairInfo',
        'FROSandBEAUS',
        'LMNaturalSelf',
        'trulesbians',
        'Mahriyahg',
        'curlartistdaria',
        'INHMD',
        'Le_Aunier',
        'misstoyokalon',
        'Naturlsnthecity',
        'DanielleReynols',
        'mahogany_care',
        'NubianNaturelle'
    ]

    # Create authentication token for the Twitter API
    from credentials import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
    from twitter_mining import oauth_login
    twitter_api = oauth_login(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    # Get timelines of input users
    timelines = get_tweets_for_users(twitter_api, input_users)



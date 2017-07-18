
import REST_utils

def check_credentials_module():
    try:
        from credentials import app_key, app_secret
        return True
    except ImportError:
        print("""
        You must create a file [credentials.py] containing:
        ```
        app_key = "smlKGxxxxxxxxxxxxxxx" # your own app key
        app_secret = "CCeKgghgup1Sxxxxxxxxxxxx" # your own app secret key
        ```
        ==> https://apps.twitter.com/
        """)
        return False


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


def get_tweets_for_users(users_screen_name=[]):
    """
    For each existing and public user in the `users_screen_name` list, get the user timeline
    Return user timelines as dict such as { user_id : list({tweets}), ...}

    Keyword args:
    `users_screen_name` list of twitter user handle (eg: potus, kanye_west,..)
    """
    user_timeline_dict = {}

    for screen_name in users_screen_name:
        screen_name_clean = preprocess_screen_name(screen_name)
        user_timeline = REST_utils.get_user_timeline(
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

    # Check that a valid credentials.py exists in the directory
    if not check_credentials_module():
        import sys
        sys.exit()

    # Get timelines of input users
    timelines = get_tweets_for_users(input_users)
    print(timelines)




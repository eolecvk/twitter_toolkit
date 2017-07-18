
import sys
import time
import datetime

from os.path import join
import simplejson as json

from urllib.error import URLError
from http.client import BadStatusLine
from twython import Twython, TwythonError
import conn

def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):
    """
    A nested helper function that handles common HTTPErrors.
    Return an updated value for wait_period if the problem is a 500 level error.
    Block until the rate limit is reset if it's a rate limiting issue (429 error).
    Returns None for 401 and 404 errors, which requires special handling by the caller.

    Keyword args:
    `max_errors` : maximum number of retries on error before exiting the function
    `*args`, `**kw` : args for twitter_api_func()
    """
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):

        if wait_period > 3600: # Seconds
            print ('Too many retries. Quitting.')
            raise e

        # See https://dev.twitter.com/docs/error-codes-responses for common codes
        if e.error_code == 401:
            print ('Encountered 401 Error (Not Authorized)')
            return None

        elif e.error_code == 404:
            print ('Encountered 404 Error (Not Found)')
            return None
        
        elif e.error_code == 429:
            print ('Encountered 429 Error (Rate Limit Exceeded)')
            if sleep_when_rate_limited:
                print ("Retrying in 15 minutes...ZzZ...")
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print ('...ZzZ...Awake now and trying again.')
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        
        elif e.error_code in (500, 502, 503, 504):
            print ('Encountered %iError. Retrying in %iseconds' %\
            (e.error_code, wait_period))
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        
        else:
            raise e
        # End of nested helper function

    wait_period = 2
    error_count = 0
    while True:
        try:
            return twitter_api_func(*args, **kw)

        except TwythonError as e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return

        except URLError as e:
            error_count += 1
            print ("URLError encountered. Continuing.")
            if error_count > max_errors:
                print ("Too many consecutive errors...bailing out.")
                raise

        except BadStatusLine as e:
            error_count += 1
            print ("BadStatusLine encountered. Continuing.")
            if error_count > max_errors:
                print ("Too many consecutive errors...bailing out.")
                raise


# =====================================================================================
# INGESTION FUNCTIONS
# =====================================================================================
from functools import partial
from sys import maxsize

def get_friends_followers_ids(
    screen_name=None, user_id=None,
    friends_limit=maxsize, followers_limit=maxsize):
    """
    For a given user, get list of followers and friends ids

    Keyword args:
    `twitter_api`: a twython.Twython authentication object
    `screen_name` or `user_id` (not both!): either user screen_name (@potus) or a user id (110123231)
    `friends_limit`: Max number of friends to return (set to 0 if only interested in getting followers)
    `followers_limit`: Max number of friends to return (set to 0 if only interested in getting friends)
    ---
    cf https://dev.twitter.com/rest/reference/get/friends/ids
    cf https://dev.twitter.com/rest/reference/get/followers/ids
    """
    
    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None),\
    "Must have screen_name or user_id, but not both"

    twitter_api = conn.get_twitter_api()

    get_followers_ids = partial(
        make_twitter_request,
        twitter_api.get_followers_ids,
        count=5000)

    get_friends_ids = partial(
        make_twitter_request,
        twitter_api.get_friends_ids,
        count=5000)

    friends_ids, followers_ids = [], []
    for twitter_api_func, limit, ids, label in [
                    [get_friends_ids, friends_limit, friends_ids, "friends"],
                    [get_followers_ids, followers_limit, followers_ids, "followers"]
                ]:
        if limit == 0:
            continue
        cursor = -1
        while cursor != 0:

            # Use make_twitter_request via the partially bound callable...
            if screen_name:
                response = twitter_api_func(screen_name=screen_name, cursor=cursor)
            else: # user_id
                response = twitter_api_func(user_id=user_id, cursor=cursor)
            
            if response is not None:

                ids.extend(response['ids'])
                cursor = response['next_cursor']
            print ('Fetched {0} total {1} ids for {2}'.format(len(ids),
                                                    label, (user_id or screen_name)))
            # XXX: You may want to store data during each iteration to provide  
            # an additional layer of protection from exceptional circumstances
            if len(ids) >= limit or response is None:
                break
    # Do something useful with the IDs, like store them to disk...
    return friends_ids[:friends_limit], followers_ids[:followers_limit]


def get_user_timeline(
    screen_name=None, user_id=None,
    since_id=None,
    max_id=None,
    tweet_limit=maxsize):
    """
    For a given user, get user_timeline

    Keyword args:
    `twitter_api`: a twython.Twython authentication object
    `screen_name` or `user_id` (not both!): either user screen_name (@potus) or a user id (110123231)
    `max_id`: id of the most recent tweet to start fetching from (get timeline goes backward in time when fetching tweets)
    `tweet_limit`: Max number of tweets to return
    ---
    https://dev.twitter.com/rest/reference/get/statuses/user_timeline
    """

    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None),\
    "Must have screen_name or user_id, but not both"
    # https://dev.twitter.com/rest/reference/get/statuses/user_timeline
    # for details on API parameters

    twitter_api = conn.get_twitter_api()

    get_user_timeline = partial(
        make_twitter_request,
        twitter_api.get_user_timeline)

    user_timeline = []

    cursor = max_id
    while cursor != 0:
    # Use make_twitter_request via the partially bound callable...
        if screen_name:
            response = get_user_timeline(screen_name=screen_name,
                since_id=since_id,
                include_rts=True,
                max_id=cursor,
                count=200)

            user_identifier = screen_name # identifier for the user 

        else: # user_id
            response = get_user_timeline(user_id=user_id,
                since_id=since_id,
                include_rts=True,
                max_id=cursor,
                count=200)

            user_identifier = user_id # identifier for the user 

        if response is None or response==[]:
            break
        else:
            ids = [t['id'] for t in response]
            cursor = min(ids)
            new_tweets = [t for t in response if t not in user_timeline]
            if new_tweets:
                user_timeline.extend(new_tweets)
                print("max_id = {cursor}".format(cursor=cursor))

            else:
                break

    return user_timeline


def get_user_data(user_id=None, screen_name=None):
    """
    For a given user, get user profile data

    Keyword args:
    `screen_name` or `user_id` (not both!): either user screen_name (@potus) or a user id (110123231)
    ---
    cf https://dev.twitter.com/rest/reference/get/users/show
    """
  
    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None),\
    "Must have screen_name or user_id, but not both"

    twitter_api = conn.get_twitter_api()
  
    get_user_data = partial(
        make_twitter_request,
        twitter_api.show_user)
    
    if user_id:
        user_data = get_user_data(user_id=user_id)
    else:
        user_data = get_user_data(screen_name=screen_name)
    
    return user_data
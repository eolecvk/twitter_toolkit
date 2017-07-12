from twython import Twython, TwythonStreamer
import time


def get_oauth_tokens(app_key, app_secret):
    """
    Supply `app_key`, `app_secret`
    Requires user to signin and confirm oauth1 to create oauth1 tokens
    get oauth1 authentication tokens: (`oauth_token`, `oauth_token_secret`)

    cf https://twython.readthedocs.io/en/latest/usage/starting_out.html#oauth1
    """
    twitter = Twython(app_key, app_secret)

    auth = twitter.get_authentication_tokens() #callback_url='oob'
    oauth_token = auth['oauth_token']
    oauth_token_secret = auth['oauth_token_secret']

    twitter = Twython(app_key, app_secret, oauth_token, oauth_token_secret)

    oauth_verifier = input(
        "1. Sign-in on Twitter.com using URL:\n{auth_url}\n\n2.Enter your pin here:".format(
        auth_url=auth['auth_url']))

    final_step = twitter.get_authorized_tokens(oauth_verifier)
    final_oauth_token = final_step['oauth_token']
    final_oauth_token_secret = final_step['oauth_token_secret']

    # Here might wanna store them to DB to avoid user authentication at every run
    return (final_oauth_token, final_oauth_token_secret)



class MyStreamer(TwythonStreamer):

    def on_success(self, data):
        """
        Defines behavior if MyStreamer() do get data
        Probably want to save to DB on success...
        """

        try:
            print("USER: {}".format(data['user']['screen_name']))
            print("DESC: {}".format(data['user']['description']))

        except KeyError as e:
            pass
            
        except Exception as e:
            print(e)


    def on_error(self, status_code, data):

        print(status_code)
        # If want to stop trying to get data because of the error:
        # self.disconnect()

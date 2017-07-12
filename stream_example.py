import twython
import stream_utils



if __name__ == "__main__":

    from credentials import app_key, app_secret
    final_oauth_token, final_oauth_token_secret = stream_utils.get_oauth_tokens(app_key, app_secret)

    stream = stream_utils.MyStreamer(app_key, app_secret, final_oauth_token, final_oauth_token_secret)

    # Tweets should be flowing at this point -- behavior of stream defined by MyStreamer.on_sucess()...
    stream.statuses.sample()






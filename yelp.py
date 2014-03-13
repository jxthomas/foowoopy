import json
import oauth2
import urllib2

class Yelp():

    def __init__(self,consumer_key, consumer_secret, token, token_secret):

        self.consumer_key = consumer_key
        self.location = 'http://api.yelp.com/v2/search'
        self.consumer = oauth2.Consumer(consumer_key, consumer_secret)
        self.token = token
        self.oauth2Token = oauth2.Token(token, token_secret)
    def getData(self,yelpRequest):
        
        # encode request
        #encoded_params = urllib.urlencode(yelpRequest)
        # unsigned URL
        url = self.location + '?' + yelpRequest ###encoded_params
        # sign the URL
        oauth_request = oauth2.Request('GET', url, {})
        oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),
                              'oauth_timestamp': oauth2.generate_timestamp(),
                              'oauth_token': self.token,
                              'oauth_consumer_key': self.consumer_key})
        oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), self.consumer, self.oauth2Token)
        signed_url = oauth_request.to_url()

        # Connect
        try:
            conn = urllib2.urlopen(signed_url, None)
            try:
                response = json.loads(conn.read())
            finally:
                conn.close()
        except urllib2.HTTPError, error:
            response = json.loads(error.read())

        return response


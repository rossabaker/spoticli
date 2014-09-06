import ssl
import string
import random
import urllib
import urllib2
import json

# Default port that Spotify Web Helper binds to.
PORT = 4371
ORIGIN_HEADER = {'Origin': 'https://open.spotify.com'}


# I had some troubles with the version of Spotify's SSL cert and Python 2.7 on
# Mac.  Did this monkey dirty patch to fix it. Your milage may vary.
def new_wrap_socket(*args, **kwargs):
    kwargs['ssl_version'] = ssl.PROTOCOL_SSLv3
    return orig_wrap_socket(*args, **kwargs)

orig_wrap_socket, ssl.wrap_socket = ssl.wrap_socket, new_wrap_socket


class SpotifyCLI(object):
    def setup(self):
        self.domain = '{0}.spotilocal.com'.format(
            ''.join(random.choice(string.ascii_lowercase) for x in range(10))
        )

        self.oauth_token = self.get_oauth_token()
        self.csrf_token = self.get_csrf_token()

    def get_oauth_token(self):
        return self.get_json('http://open.spotify.com/token')['t']

    def get_csrf_token(self):
        # Requires Origin header to be set to generate the CSRF token.
        ret = self.get_json('/simplecsrf/token.json', headers=ORIGIN_HEADER)
        return ret['token']

    def get_json(self, url, params={}, headers={}):
        if url.startswith('/'):
            url = "https://%s:%d%s" % (self.domain, PORT, url)

        if params:
            url += "?" + urllib.urlencode(params)

        request = urllib2.Request(url, headers=headers)
        return json.loads(urllib2.urlopen(request).read())

    def get_version(self):
        return self.get_json(
            '/service/version.json',
            params={'service': 'remote'},
            headers=ORIGIN_HEADER
        )

    def get_status(self):
        params = {
            'oauth': self.oauth_token,
            'csrf': self.csrf_token,
        }
        return self.get_json(
            '/remote/status.json',
            params=params,
            headers=ORIGIN_HEADER
        )

    def pause(self, pause=True):
        params = {
            'oauth': self.oauth_token,
            'csrf': self.csrf_token,
            'pause': 'true' if pause else 'false'
        }
        self.get_json(
            '/remote/pause.json',
            params=params,
            headers=ORIGIN_HEADER
        )

    def unpause(self):
        self.pause(pause=False)

    def play(self, spotify_uri):
        params = {
            'oauth': self.oauth_token,
            'csrf': self.csrf_token,
            'uri': spotify_uri,
            'context': spotify_uri,
        }
        self.get_json(
            '/remote/play.json',
            params=params,
            headers=ORIGIN_HEADER
        )

if __name__ == '__main__':
    spotify = SpotifyCLI()
    spotify.setup()

    import pprint
    pprint.pprint(spotify.get_status())

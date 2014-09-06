import string
import random
import urllib
import urllib2
import json

# Default port that Spotify Web Helper binds to.
PORT = 4371


class SpotifyCLI(object):
    oauth_token = None
    csrf_token = None

    def setup(self):
        self.domain = '{0}.spotilocal.com'.format(
            ''.join(random.choice(string.ascii_lowercase) for x in range(10))
        )

        self.oauth_token = self.get_oauth_token()
        self.csrf_token = self.get_csrf_token()

    def get_oauth_token(self):
        return self.get('http://open.spotify.com/token')['t']

    def get_csrf_token(self):
        ret = self.get('/simplecsrf/token.json')
        return ret['token']

    def get(self, url, params={}, headers={}):
        if url.startswith('/'):
            url = "https://%s:%d%s" % (self.domain, PORT, url)

        # Always add the default parameters and headers
        params.update({
            'oauth': self.oauth_token,
            'csrf': self.csrf_token,
        })
        headers.update({
            'Origin': 'https://open.spotify.com'
        })

        url += "?" + urllib.urlencode(params)

        request = urllib2.Request(url, headers=headers)
        return json.loads(urllib2.urlopen(request).read())

    def get_version(self):
        return self.get('/service/version.json', {'service': 'remote'})

    def get_status(self):
        return self.get('/remote/status.json')

    def pause(self, pause=True):
        pause = 'true' if pause else 'false'
        self.get('/remote/pause.json', {'pause': pause})

    def unpause(self):
        self.pause(pause=False)

    def play(self, spotify_uri):
        self.get('/remote/play.json', {
            'uri': spotify_uri,
            'context': spotify_uri
        })

if __name__ == '__main__':
    spotify = SpotifyCLI()
    spotify.setup()

    import pprint
    pprint.pprint(spotify.get_status())

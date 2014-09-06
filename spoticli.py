import string
import random
import json
import requests

# Default port that Spotify Web Helper binds to.
PORT = 4371


class SpotifyCLI(object):
    oauth_token = None
    csrf_token = None

    def setup(self):
        self.domain = '{0}.spotilocal.com'.format(
            ''.join(random.choice(string.ascii_lowercase) for x in range(10))
        )

        self.oauth_token = self.get('http://open.spotify.com/token')['t']
        self.csrf_token = self.get('/simplecsrf/token.json')['token']

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

        request = requests.get(url, params=params, headers=headers)
        return request.json()

    def get_status(self):
        return self.get('/remote/status.json')

    def pause(self, pause=True):
        return self.get('/remote/pause.json', {'pause': json.dumps(pause)})

    def unpause(self):
        return self.pause(pause=False)

    def play(self, spotify_uri):
        return self.get('/remote/play.json', {
            'uri': spotify_uri,
            'context': spotify_uri
        })

if __name__ == '__main__':
    spotify = SpotifyCLI()
    spotify.setup()

    import pprint
    pprint.pprint(spotify.get_status())

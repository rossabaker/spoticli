import string
import random
import json
import requests
import re
import ssl

# Default port that Spotify Web Helper binds to.
PORT = 4371

class SpotifyCLI(object):
    oauth_token = None
    csrf_token = None

    def setup(self):
        self.domain = '{0}.spotilocal.com'.format(
            ''.join(random.choice(string.ascii_lowercase) for x in range(10))
        )
        #changed url endpoints
        self.oauth_token = self.get('https://embed.spotify.com/remote-control-bridge/')
        self.csrf_token = self.get('/simplecsrf/token.json')['token']

    def get(self, url, params={}, headers={}):
        response = ""
        isCSRF = False
        
        if url.startswith('/'):
            url = "https://%s:%d%s" % (self.domain, PORT, url)
            isCSRF = True

        # Always add the default parameters and headers
        params.update({
            'oauth': self.oauth_token,
            'csrf': self.csrf_token,
        })
        #headers also needed to be changed
        headers.update({
            'Referer':'https://embed.spotify.com/remote-control-bridge/',
            'Origin': 'https://embed.spotify.com/'
        })
        #SSL verification is currently set to false because Im currently unable to figure out why its refusing the certificate
        request = requests.get(url, params=params, headers=headers, verify= False)
        
        if isCSRF:
            response = request.json()
        else:
            data = request.text
            search = re.compile('(?<=a = \')(.*)(?=\';)')
            parsed = search.findall(data)
            response = parsed[0]
            
        return response  
        

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

    #spotify.play("spotify_uri")

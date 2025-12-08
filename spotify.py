import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']): #type: ignore
    track = item['track']
    print(idx, track['artists'][0]['name'], " - ", track['name'])

class Spotify():
    def __init__(self, gui):
        super().__init__()
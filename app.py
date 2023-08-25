from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session  
import spotipy 
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = 'XX'
CLIENT_SECRET = 'XX'

app = Flask(__name__)
app.secret_key = CLIENT_SECRET

app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.config['SPOTIPY_CLIENT_ID'] = CLIENT_ID
app.config['SPOTIPY_CLIENT_SECRET'] = CLIENT_SECRET
app.config['SPOTIPY_REDIRECT_URI'] = 'http://localhost:5000/callback'

sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri='http://localhost:5000/callback',
                        scope='playlist-read-private, playlist-read-collaborative, playlist-modify-private, playlist-modify-public, user-library-modify, user-library-read')

@app.route('/')
def index():
    if 'access_token' in session:
        sp = spotipy.Spotify(auth=session['access_token'])
        user_info = sp.me()
        playlists = sp.current_user_playlists()
        return render_template('index.html', user_info=user_info, playlists=playlists)
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['access_token'] = token_info['access_token']
    return redirect(url_for('index'))

@app.route('/ordenar/<playlist_id>')
def ordenar(playlist_id):
    if 'access_token' in session:
        sp = spotipy.Spotify(auth=session['access_token'])
        playlist = sp.playlist_tracks(playlist_id)
        
        sorted_tracks = sorted(playlist['items'], key=lambda x: x['track']['popularity'], reverse=True)
        track_uris = [track['track']['uri'] for track in sorted_tracks]
        
        user_info = sp.me()
        new_playlist_name = f"Ordenada playlist"
        new_playlist = sp.user_playlist_create(user_info['id'], new_playlist_name, public=False)
        sp.user_playlist_add_tracks(user_info['id'], new_playlist['id'], track_uris)
        
        return redirect(url_for('index'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import requests
import tomllib
import os
import sys
import time
from croniter import croniter
from datetime import datetime
from flask import Flask, request
from threading import Thread

def load_config(file_path):
    try:
        with open(file_path, 'rb') as f:
            return tomllib.load(f)
    except Exception as e:
        print(f"Error loading configuration file: {e}")
        raise

def save_config(config, file_path):
    try:
        with open(file_path, 'wb') as f:
            f.write(tomllib.dumps(config).encode())
    except Exception as e:
        print(f"Error saving configuration file: {e}")
        raise

def ensure_directory(directory_path):
    if not os.path.exists(directory_path):
        print(f"Directory '{directory_path}' does not exist. Creating it.")
        os.makedirs(directory_path)
    else:
        print(f"Directory '{directory_path}' exists.")

def start_oauth_server(client_id, client_secret, redirect_uri, scope):
    app = Flask(__name__)

    sp_oauth = SpotifyOAuth(client_id=client_id,
                            client_secret=client_secret,
                            redirect_uri=redirect_uri,
                            scope=scope)

    @app.route('/')
    def home():
        auth_url = sp_oauth.get_authorize_url()
        return f'''
        <h1>Spotify OAuth</h1>
        <p>Click the button below to authorize:</p>
        <a href="{auth_url}"><button>Authorize Spotify</button></a>
        '''

    @app.route('/callback')
    def callback():
        code = sp_oauth.parse_auth_response_url(request.url)
        if not code:
            return "Error: No authorization code received.", 400

        try:
            sp_oauth.get_access_token(code, as_dict=False)
        except Exception as e:
            print(f"Error getting token: {e}")
            return '''<h1>Spotify OAuth Failure!</h1>'''

        return '''
        <h1>Spotify OAuth Successful!</h1>
        <p>Refresh token saved. The cron task will now use this token.</p>
        '''

    print("Starting OAuth server at http://localhost:8888")
    app.run(host='0.0.0.0', port=8888)

def export_playlists(config):
    ensure_directory(config['results_dir'])

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config['client_id'],
                                                client_secret=config['client_secret'],
                                                redirect_uri=config['redirect_uri'],
                                                scope="playlist-read-private playlist-read-collaborative",
                                                open_browser=False))
    tracks_data = []
    playlist_data = []
    playlists = sp.current_user_playlists()
    while playlists:
        for playlist in playlists['items']:
            print(f"Fetching tracks for playlist: {playlist['name']}")
            
            playlist_data.append({
                'Playlist ID': playlist['id'],
                'Playlist Name': playlist['name'],
                'Playlist Description': playlist['description'],
                'Playlist Owner': playlist['owner']['display_name'],
            })

            tracks = sp.playlist_tracks(playlist['id'])
            while tracks:
                for item in tracks['items']:
                    track = item['track']
                    tracks_data.append({
                        'Playlist ID': playlist['id'],
                        'Track ID': track['id'],
                        'Track Name': track['name'],
                        'Artist(s)': ', '.join(artist['name'] for artist in track['artists']),
                        'Album': track['album']['name'],
                        'Album Release Date': track['album']['release_date'],
                    })
                
                if tracks['next']:
                    tracks = sp.next(tracks)
                else:
                    tracks = None

        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None

    df = pd.DataFrame(playlist_data)
    output_file = os.path.join(config['results_dir'], 'spotify_playlists.csv')
    df.to_csv(output_file, index=False)
    print(f"Playlists exported to {output_file}")

    df = pd.DataFrame(tracks_data)
    output_file = os.path.join(config['results_dir'], 'spotify_tracks.csv')
    df.to_csv(output_file, index=False)
    print(f"Tracks exported to {output_file}")

    if config.get('ping_url'):
        response = requests.get(config['ping_url'])
        if response.status_code == 200:
            print("Ping successful!")
        else:
            print(f"Ping failed with status code: {response.status_code}")

def run_cron_task(config, cron_expression):
    cron = croniter(cron_expression, datetime.now())
    next_run = cron.get_next(datetime)
    print(f"Scheduled next run at: {next_run}")
    
    while True:
        now = datetime.now()
        if now >= next_run:
            print("Running the export task...")
            try:
                export_playlists(config)
            except Exception as e:
                print(f"An error occurred: {e}")
            next_run = cron.get_next(datetime)
            print(f"Scheduled next run at: {next_run}")
        time.sleep(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python export_spotify.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]
    config = load_config(config_file)

    # Start OAuth server in a separate thread
    oauth_thread = Thread(target=start_oauth_server, args=(
        config['client_id'], config['client_secret'], config['redirect_uri'],
        "playlist-read-private playlist-read-collaborative"
    ))
    oauth_thread.daemon = True
    oauth_thread.start()

    # Run the cron task
    cron_expression = config.get('schedule', {}).get('cron', "0 1 * * *")
    print(f"Using cron expression: {cron_expression}")
    run_cron_task(config, cron_expression)

if __name__ == "__main__":
    main()
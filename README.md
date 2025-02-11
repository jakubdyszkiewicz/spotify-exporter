# Spotify Exporter
A Python tool to export Spotify playlists and save them as CSV files. This script also supports scheduling exports using cron expressions.

## Why?
I want to keep a backup of my playlists in case Spotify decides to cut the access to my account.
I run this at schedule on my homelab using Docker containers.
Currently, I have 239 playlist so that's the data I tested it on.

## Features
- Export Spotify playlists to CSV format.
- Schedule automatic exports using cron expressions.
- Ping a URL (I recommend https://healthchecks.io/) upon successful export to track if script works or not

## Requirements
- Python 3.11+
- A Spotify Developer account with `client_id` and `client_secret`. It's free.

## Authentication
The most annoying part is authentication. Creating an app and acquiring `client_id` and `client_secret` is not a full story.
You also need to authenticate as a user using OAuth flow within the app that you created. This requires user interaction.
Spotipy offers two ways of doing this. It either opens a browser or requires input on stdin.
Both does not work well inside a docker container, especially when running on the server.
This project instead starts a server at port 8888 that serves HTML page with a link to auth in Spotify.
To finish the authentication, it expects callback at `<address>:8888/callback` to finish auth.

When you create an app in Spotify, the redirect URL has to be the same value as in `config.toml`.
If you are starting out on localhost, it can be just `http://localhost:8888/callbacks`

The good news is that once you authenticate it preserves the data quite well.
Long lived refresh token is stored in `/app/auth-cache` by default.
If you plan to recreate container a lot, consider mounting a volume for it, but keep in mind it contains credentials.

## Running
1) Update `config.toml` with schedule and app secret.
2) Run the app

### Docker
```
docker run \
  -e TZ=Europe/Warsaw \
  -v $(pwd)/out:/app/data \
  -v $(pwd)/auth-cache:/app/auth-cache \
  -v $(pwd)/config.toml:/app/config.toml \
  -p 8888:8888 \
  jakubdyszkiewicz/spotify-exporter:latest
```
Change the [timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones), otherwise the Cron might surprise you.
For a real use, replace `:latest` with the tag. I can't promise non-breaking changes. It's just a fun side project.

### Python
```bash
git clone https://github.com/jakubdyszkiewicz/spotify-exporter.git
cd spotify-exporter

python3 -m venv .venv
source .venv/bin/activate
# source .venv/bin/activate.fish for fish shell

pip3 install -r requirements.txt

python3 spotify-exporter.py config.toml
```

3) Go to `localhost:8888` to complete auth flow.
4) Wait for the data

### Sample output
```
$ cat out/spotify_playlists.csv
Playlist ID,Playlist Name,Playlist Description,Playlist Owner
1CWQLr0tVfvbqVBTX1QPxZ,My top tracks playlist,Playlist created by the tutorial on developer.spotify.com,Jakub Dyszkiewicz

$ cat out/spotify_tracks.csv
Playlist ID,Track ID,Track Name,Artist(s),Album,Album Release Date
1CWQLr0tVfvbqVBTX1QPxZ,11AGQ5cmFyHalx9tsAVkkA,BTS,Chromeo,Adult Contemporary,2024-02-16
```

## Limitations
Most of my playlists are stored in folders. Sadly, there is no API to retrieve folder for each playlist.

## Is it possible to also export XYZ?
Sure, PRs are welcomed!
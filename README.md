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
- A Spotify Developer account with `client_id` and `client_secret`.

## Limitations
Most of my playlists are stored in folders. Sadly, there is no API to retrieve folder for each playlist.  

## Installation
```bash
git clone https://github.com/jakubdyszkiewicz/spotify-exporter.git
cd spotify-exporter

python3 -m venv .venv
source .venv/bin/activate

pip3 install -r requirements.txt
```

## Running
Update config.toml with your files
```
python3 spotify-exporter.py config.toml
```

## Sample output
```
$ cat out/spotify_playlists.csv
Playlist ID,Playlist Name,Playlist Description,Playlist Owner
1CWQLr0tVfvbqVBTX1QPxZ,My top tracks playlist,Playlist created by the tutorial on developer.spotify.com,Jakub Dyszkiewicz

$ cat out/spotify_tracks.csv
Playlist ID,Track ID,Track Name,Artist(s),Album,Album Release Date
1CWQLr0tVfvbqVBTX1QPxZ,11AGQ5cmFyHalx9tsAVkkA,BTS,Chromeo,Adult Contemporary,2024-02-16
```

## Docker
Building
```
docker build -t spotify-exporter .
```

Running
```
docker run \
  -e TZ=Europe/Warsaw \
  -v $(pwd)/out:/app/data \
  -v $(pwd)/my-config.toml:/app/config.toml \
  -p 8888:8888 \
  spotify-exporter
```


spotify-sort-by-release [![Spotify](https://i.imgur.com/mbV7rfR.png)](https://spotify.com)
==========================================================================================

![forthebadge](https://forthebadge.com/images/badges/built-with-swag.svg)

It's ~2019~ 2020 and [Spotify](https://spotify.com) still doesn't support sorting playlists by release date of tracks. This simple tool uses Spotify Web API to sort a playlist in this way.

## Requirements

- [Requests](https://python-requests.org).

## Installing

Clone the repository

```sh
git clone --recurse-submodules https://github.com/mcieno/spotify-sort-by-release.git
cd spotify-sort-by-release
```

Install requirements

```sh
pip install -r requirements.txt
```

Install `spotify-sort-by-release`

```sh
pip install .
```

## Usage

You can use `spotify-sort-by-release` as a command line tool.

- `spotify-sort-by-release library`: sorts the library
- `spotify-sort-by-release playlist`: sorts a playlist

You'll need an _OAuth Token_ to contact the Spotify Web API, indeed. Make sure you request a token with permissions to create playlists for your account or to edit your library.

The script will create a new playlist and insert tracks into it sorted by release date, so that the _"custom order"_ of the playlist is the desired one.

[![asciicast](https://i.imgur.com/t1Ir1td.gif)](https://asciinema.org/a/oVmPm2CyreVNyWgFcE3sdaPXu)

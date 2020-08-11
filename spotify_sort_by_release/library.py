#!/usr/bin/env python3
# -*- coding: utf8 -*-
import json
import requests
import time

from . import session


def get_tracks() -> list:
    '''Get user library (saved tracks).


    Returns
    -------
    list
        List of tracks. Each track is a dictionary as per the Spotify Web API documentation.
    '''

    all_tracks = []

    # We use the same approach used in `get_my_playlists()` to make sure we
    # retrieve all the playlists.
    next_url = F"https://api.spotify.com/v1/me/tracks"

    while next_url:
        response = session.s.get(next_url)
        assert response.status_code is requests.codes.OK, response.text

        response_json = json.loads(response.text)

        all_tracks.extend(map(lambda i: i['track'], response_json['items']))
        next_url = response_json['next']

    return all_tracks


def save_tracks(tracks: list, threshold: int = 3) -> None:
    '''Save given Tracks to the library.


    Parameters
    ----------
    tracks : list
        List of Tracks, as per the Spotify Web API documentation.

    threshold : int
        Maximum number of tracks to put at once. Order may not be preserved
        among these tracks, so the greater the value, the more tracks will be
        scrambled. Defaults to 3. Must not be greater than 100.
    '''

    tracks_uris = list(map(lambda t: t['uri'].split(':')[-1], tracks))

    # Ensure the threshold is in the correct range
    assert 1 <= threshold <= 100, F"Bad threshold value: {threshold}"

    # Cannot add all tracks at once, so make multiple API calls.
    MAX_TRACKS = int(threshold)
    for uris_chunk in map(lambda i: tracks_uris[i:i + MAX_TRACKS],
                          range(0, len(tracks_uris), MAX_TRACKS)):

        print(F'[*] Saving tracks {i} to {i + MAX_TRACKS - 1} of {MAX_TRACKS}',
              end='    \r')

        response = session.s.put(
            F"https://api.spotify.com/v1/me/tracks",
            data=json.dumps({'ids': uris_chunk}))

        assert response.status_code is requests.codes.OK, response.text


        time.sleep(.1)  # No DoS


def delete_tracks(tracks: list) -> None:
    '''Delete all occurrences of given Tracks from the library.


    Parameters
    ----------
    tracks : list
        List of Tracks, as per the Spotify Web API documentation.
    '''
    # Drop duplicates from tracks to avoid overloading the endpoint.
    tracks_uris = set(map(lambda t: t['uri'], tracks))
    # Prepare the objects as the API expects them.
    tracks_objs = list(map(lambda t: t.split(':')[-1], tracks_uris))

    # Cannot delete all tracks at once, so make multiple API calls.
    MAX_TRACKS = 50
    for uris_chunk in map(lambda i: tracks_objs[i:i + MAX_TRACKS],
                          range(0, len(tracks_objs), MAX_TRACKS)):

        q = F"ids={','.join(uris_chunk)}"
        response = session.s.delete(
            F"https://api.spotify.com/v1/me/tracks?{q}")

        assert response.status_code is requests.codes.OK, response.text

        time.sleep(.1)  # No DoS


if __name__ == '__main__':
    import argparse
    try:
        from pprint import pprint
    except ImportError:
        pprint = print

    parser = argparse.ArgumentParser('Test playlists API.')
    parser.add_argument('-oauth', type=str, required=True, help="OAuth Token")
    args = parser.parse_args()

    session.init(args.oauth)

    pprint(get_tracks())

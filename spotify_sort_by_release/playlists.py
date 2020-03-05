#!/usr/bin/env python3
# -*- coding: utf8 -*-
import json
import requests
import time

from . import session


def get_playlist(playlist_id : str) -> dict:
    '''Get a Playlist.


    Parameters
    ----------
    playlist_id : str
        Identifier of the playlist.


    Returns
    -------
    dict
        The playlist, as per the Spotify Web API documentation.
    '''
    response = session.s.get(
        F"https://api.spotify.com/v1/playlists/{playlist_id}")
    assert response.status_code is requests.codes.OK, response.text

    return json.loads(response.text)


def get_my_playlists() -> list:
    '''Get a List of Current User's Playlists.


    Returns
    -------
    list
        List of playlists. Each playlist is a dictionary as per the Spotify Web
        API.
    '''

    all_playlists = []

    # We must loop because the number of playlists the API will return is
    # limited. Hence some playlists may be missing.
    # To retrieve all playlists we'll use the fact that the response will
    # contain the key `next`, whose value is the URL to GET for the missing
    # playlists. When we reach the end of this "linked list", `next` will be
    # None, so the loop terminates.
    next_url = F"https://api.spotify.com/v1/me/playlists"

    while next_url:
        response = session.s.get(next_url)
        assert response.status_code is requests.codes.OK, response.text

        response_json = json.loads(response.text)

        all_playlists.extend(response_json['items'])
        next_url = response_json['next']

    return all_playlists


def get_user_playlists(user_id : str) -> list:
    '''Get a List of a User's Playlists.


    Parameters
    ----------
    user_id : str
        Identifier of the user.


    Returns
    -------
    list
        List of playlists. Each playlist is a dictionary as per the Spotify Web
        API.
    '''

    all_playlists = []

    # We use the same approach used in `get_my_playlists()` to make sure we
    # retrieve all the playlists.
    next_url = F"https://api.spotify.com/v1/users/{user_id}/playlists"

    while next_url:
        response = session.s.get(next_url)
        assert response.status_code is requests.codes.OK, response.text

        response_json = json.loads(response.text)

        all_playlists.extend(response_json['items'])
        next_url = response_json['next']

    return all_playlists


def get_playlist_tracks(playlist_id : str) -> list:
    '''Get a Playlist's Tracks.


    Parameters
    ----------
    playlist_id : str
        Identifier of the playlist.


    Returns
    -------
    list
        List of tracks. Each track is a dictionary as per the Spotify Web API documentation.
    '''

    all_tracks = []

    # We use the same approach used in `get_my_playlists()` to make sure we
    # retrieve all the playlists.
    next_url = F"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    while next_url:
        response = session.s.get(next_url)
        assert response.status_code is requests.codes.OK, response.text

        response_json = json.loads(response.text)

        all_tracks.extend(map(lambda i: i['track'], response_json['items']))
        next_url = response_json['next']

    return all_tracks


def create_playlist(playlist_data : str) -> dict:
    '''Create a Playlist.


    Parameters
    ----------
    playlist_data : dict
        Dictionary containing the details of the playlist to be created:
            - name (string): Required. The name for the new playlist.

            - public (boolean): Optional. Defaults to `True`. If `True` the
                                playlist will be public.

            - collaborative (boolean): Optional. Defaults to `False`. If `True`
                                       the playlist will be collaborative.

            - description (string): Optional. Value for playlist description.


    Returns
    -------
    dict
        The playlist created, as per the Spotify Web API documentation.


    Examples
    --------
    Create a public playlist:

        ```
        playlist_data = {
            'name': 'My Public Playlist',
            'public': True,
            'description': 'Good vibes only.'
        }
        create_playlist(playlist_data)
        ```
    '''
    response = session.s.post(F"https://api.spotify.com/v1/me/playlists",
                              data=json.dumps(playlist_data))
    assert response.status_code in (
        requests.codes.OK, requests.codes.CREATED), response.text

    return json.loads(response.text)


def add_tracks(playlist_id : str, tracks : list, threshold : int = 10) -> None:
    '''Add Tracks to a Playlist.


    Parameters
    ----------
    playlist_id : str
        Identifier of the playlist.

    tracks : list
        List of tracks to add, as per the Spotify Web API documentation.

    threshold : int
        Maximum number of tracks to put at once. Order may not be preserved
        among these tracks, so the greater the value, the more tracks will be
        scrambled. Defaults to 10. Must not be greater than 100.
    '''

    tracks_uris = list(map(lambda t: t['uri'], tracks))

    # Ensure the threshold is in the correct range
    assert 1 <= threshold <= 100, F"Bad threshold value: {threshold}"

    # Cannot add all tracks at once, so make multiple API calls.
    MAX_TRACKS = int(threshold)
    for uris_chunk in map(lambda i: tracks_uris[i:i + MAX_TRACKS],
                          range(0, len(tracks_uris), MAX_TRACKS)):

        q = F"uris={','.join(uris_chunk)}"
        response = session.s.post(
            F"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?{q}")
        assert response.status_code is requests.codes.CREATED, response.text

        time.sleep(.1) # No DoS


def delete_tracks(playlist_id: str, tracks: list) -> None:
    '''Delete all occurrences of given Tracks from a Playlist.


    Parameters
    ----------
    playlist_id : str
        Identifier of the playlist.

    tracks: list
        List of Tracks, as per the Spotify Web API documentation.
    '''
    # Drop duplicates from tracks to avoid overloading the endpoint.
    tracks_uris = set(map(lambda t: t['uri'], tracks))
    # Prepare the objects as the API expects them.
    tracks_objs = list(map(lambda uri: {'uri': uri}, tracks_uris))

    # Cannot delete all tracks at once, so make multiple API calls.
    MAX_TRACKS = 100
    for uris_chunk in map(lambda i: tracks_objs[i:i + MAX_TRACKS],
                          range(0, len(tracks_objs), MAX_TRACKS)):

        response = session.s.delete(
            F"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
            data=json.dumps({'tracks': uris_chunk}))

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

    pprint(get_my_playlists())

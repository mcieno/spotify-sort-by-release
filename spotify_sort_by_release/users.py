#!/usr/bin/env python3
# -*- coding: utf8 -*-
import json
import requests

from . import session


def get_current_user() -> dict:
    '''Get Current User's Profile.


    Returns
    -------
    dict
        The current user, as per the Spotify Web API documentation.
    '''
    response = session.s.get('https://api.spotify.com/v1/me')
    assert response.status_code is requests.codes.OK, response.text

    return json.loads(response.text)


def get_user(user_id : str) -> dict:
    '''Get a User's Profile.


    Parameters
    ----------
    user_id : str
        Identifier of the user.


    Returns
    -------
    dict
        The user, as per the Spotify Web API documentation.
    '''
    response = session.s.get(F"https://api.spotify.com/v1/users/{user_id}")
    assert response.status_code is requests.codes.OK, response.text
    return json.loads(response.text)


if __name__ == '__main__':
    import argparse
    try:
        from pprint import pprint
    except ImportError:
        pprint = print

    parser = argparse.ArgumentParser('Test users API.')
    parser.add_argument('-oauth', type=str, required=True, help="OAuth Token")
    args = parser.parse_args()

    session.init(args.oauth)

    pprint(get_current_user())

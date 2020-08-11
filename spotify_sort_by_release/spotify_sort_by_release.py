#!/usr/bin/env python3
# -*- coding: utf8 -*-
import argparse
import json
import requests

from . import library
from . import playlists
from . import session
from . import users


def track_sorting_key(t : dict) -> str:
    '''Get the sorting key for a track.
    Tracks are sorted primarly by release date. In case of collisions, the
    relevant keys are the album name, the artist's name and the track name.


    Parameters
    ----------
    t : dict
        The track, as per the Spotify Web API documentation.


    Returns
    -------
    str
        The sorting key for the given track.
    '''
    release_date = t['album']['release_date']
    artist_name = t['album']['artists'][0]['name']
    album_name = t['album']['name']
    track_name = t['name']

    return F"{release_date} | {album_name} | {artist_name} | {track_name}"


def sort_library_by_release(args) -> None:
    '''Sort a playlist by release date of tracks. A new playlist is created,
    and tracks are added to it in correct order.


    Parameters
    ----------
    args : Namespace
        Namespace containing the following information:
            - reversed (boolean): If `True`, tracks will be sorted in reversed
                                  order: oldest to latest.
            - threshold (int): Number of songs that could be added together.
                               For example, if `args.threshold = 5`, then songs
                               will be added in chunks of 5. The bigger the
                               threshold the faster the process, but note that
                               songs inside a chunk might end up in random order.
            - backup (boolean): If `True`, create a playlist to backup the library
                                before sorting.
    '''
    # Read all tracks from library and sort them.
    tracks = library.get_tracks()
    tracks = sorted(tracks, key=track_sorting_key, reverse=args.reversed)

    print('\n'.join(track_sorting_key(track) for track in tracks))

    # Delete all tracks from library
    print(F"\n Will delete all tracks from the library and "
          F"then try to insert them back in sorted order.")

    if input(' Continue? (y/[N]) ').strip()[:1] not in ('y', 'Y'):
        raise KeyboardInterrupt()

    if args.backup:
        library_backup_playlist_name = 'Your Library [Backup]'
        print(F"[+] Backing up library into playlist \"{library_backup_playlist_name}\"")

        destination_playlist = playlists.create_playlist(
            {'name': library_backup_playlist_name, 'description': '', 'public': False})

        # Add all tracks
        playlists.add_tracks(destination_playlist['id'], tracks)

    print(F"[+] Deleting tracks from library")
    library.delete_tracks(tracks)

    # Add all tracks to library in correct order
    print(F"[+] Adding tracks back into library")
    library.save_tracks(tracks, threshold=args.threshold)


def sort_playlist_by_release(args) -> None:
    '''Sort a playlist by release date of tracks. A new playlist is created,
    and tracks are added to it in correct order.


    Parameters
    ----------
    args : Namespace
        Namespace containing the following information:
            - playlist (dict): The playlist to be sorted, as per the Spotify
                               Web API documentation.
            - name (string): Name for the destination playlist.
            - description (string): Description for the destination playlist.
            - reversed (boolean): If `True`, tracks will be sorted in reversed
                                  order: oldest to latest.
    '''
    # Read all tracks from source playlist and sort them.
    tracks = playlists.get_playlist_tracks(args.playlist['id'])
    tracks = sorted(tracks, key=track_sorting_key, reverse=not args.reversed)

    if args.inplace:
        # If sorting is to be done in-place, the destination playlist is simply
        # the same as the source playlist.
        print(F"\n Will delete all tracks from {args.playlist['name']} and "
              F"then try to insert them back in sorted order.")

        if input(' Continue? (y/[N]) ').strip()[:1] not in ('y', 'Y'):
            raise KeyboardInterrupt()

        playlists.delete_tracks(args.playlist['id'], tracks)
        destination_playlist = args.playlist

    else:
        # If sorting is not in-place, attempt to create the new playlist.
        # This action may fail if the provided OAuth Token wasn't generated
        # with the correct privileges.
        print((F"\n Will copy tracks from {args.playlist['name']} into new "
               F"playlist {args.name} (description: '{args.description}')"))

        if input(' Continue? (y/[N]) ').strip()[:1] not in ('y', 'Y'):
            raise KeyboardInterrupt()

        destination_playlist = playlists.create_playlist(
            {'name': args.name, 'description': args.description, 'public': False})

    # Add all tracks
    playlists.add_tracks(destination_playlist['id'], tracks)


def do_library(args) -> None:
    '''Handler for sub-command `library`.


    Parameters
    ----------
    args : Namespace
        Namespace from `main`
    '''
    # Sort whole library is lit but risky, make sure the user understands.
    if not args.backup:
        print(' Remember to backup your library before sorting!')

        if input(' Continue anyway? (y/[N]) ').strip()[:1] not in ('y', 'Y'):
            raise KeyboardInterrupt()

    # Profit
    sort_library_by_release(args)


def do_playlist(args) -> None:
    '''Handler for sub-command `playlist`.


    Parameters
    ----------
    args : Namespace
        Namespace from `main`
    '''
    # Sort in-place is lit but risky, make sure the user understands.
    if args.inplace:
        print(' Remember to backup your playlist before sorting in-place!')
        if input(' Continue anyway? (y/[N]) ').strip()[:1] not in ('y', 'Y'):
            raise KeyboardInterrupt()

    # Let user interactively choose the playlist to sort
    if not args.playlist:
        print(" Playlist ID missing.")
        print("   1) Search my playlists")
        print("   2) Search user's playlists")

        choice = None
        while choice not in ('1', '2'):
            choice = input('  > ').strip()

        if choice is '1':
            available_playlists = playlists.get_my_playlists()
        else:
            user_id = None
            while not user_id:
                user_id = input(' Insert target user\'s ID: ').strip()
            available_playlists = playlists.get_user_playlists(user_id)

        print(' Choose target playlist:')
        for i, p in enumerate(available_playlists):
            print(F"   {i+1:4d}) {p['name']:32.32}    [ID: {p['id']}]")
        while not args.playlist:
            choice = input('   > ')
            try:
                choice = int(choice)
                args.playlist = available_playlists[choice - 1]
            except (ValueError, IndexError):
                pass
    else:
        # Convert ID to the actual playlist item
        args.playlist = playlists.get_playlist(args.playlist)

    if not args.inplace:
        # Let user pick name/description for the new, sorted, playlist
        if not args.name:
            print(' Missing new playlist name.')
            default_name = F"SORTED: {args.playlist['name']}"
            args.name = input(F"   [Default: '{default_name}']> ").strip() \
                or default_name

        if args.description is None:
            print(' Missing new playlist description.')
            default_description = args.playlist.get('description', '')
            args.description = input(
                F"   [Default: '{default_description}']> ").strip() \
                or default_description

    # Profit
    sort_playlist_by_release(args)


def main() -> None:
    print("""\033[1;92m
                                          ..-::::::--.
                                     `-/+oooooooooooooo+/-`
                                   ./oooooooooooooooooooooo/.
                                 .+oooooooooooooooooooooooooo+-
                               `/oooooooooooooooooooooooooooooo/`
                              `+oooooo+///::::::://++oooooooooooo`
                             `+ooo+.                  `.-:/ooooooo`
                             /ooooo.`.--:://////:::-..`     .:oooo/
                            `oooooooooooooo++++ooooooooo/:.  `ooooo`
                            .ooooooo:-.`          `.-:/+ooooooooooo-
                            .ooooooo-`.--::////::--.`   `./oooooooo-
                            `ooooooooooooooooooooooooo/:.  /ooooooo`
                             /ooooooo:-.```    ``..-:+oooooooooooo+
                             `ooooooo--:://++++//:-.`  .:ooooooooo`
                              .ooooooooooooooooooooooo/-:oooooooo.
                               `+oooooooooooooooooooooooooooooo+`
                                 -oooooooooooooooooooooooooooo:
                                   -+oooooooooooooooooooooo+:`
                                     `:+oooooooooooooooo+:.
                                         `-:://////::-`

    \033[0m""")

    parser = argparse.ArgumentParser('Test playlists API.')

    parser.add_argument('-o', '--oauth', type=str, default=None,
                        help='OAuth Token')
    parser.add_argument('--reversed', action='store_true', default=False,
                        help='Sort from oldest to newest')

    subparsers = parser.add_subparsers(help='sub-command help', dest='command')

    # Subparser for library sorting
    parser_l = subparsers.add_parser('library', help='Sort user library')

    parser_l.add_argument('--threshold', type=int, default=3,
                          help='Maximum number of tracks to add at once')

    parser_l.add_argument('--backup', action='store_true', default=False,
                          help='Backup your library before sorting')

    # Subparser for playlist sorting
    parser_p = subparsers.add_parser('playlist', help='Sort a playlist')

    parser_p.add_argument('-p', '--playlist', type=str, default=None,
                          help='Playlist ID of the playlist to sort')
    parser_p.add_argument('-n', '--name', type=str, default=None,
                          help='Name of the new playlist with sorted tracks')
    parser_p.add_argument('-d', '--description', type=str, default=None,
                          help='Description of the new playlist')
    parser_p.add_argument('--inplace', action='store_true', default=False,
                          help='Sort playlist in-place.')

    args = parser.parse_args()


    try:
        # OAuth Token is required by almost every API call, so user can't omit it.
        if not args.oauth:
            print(' OAuth Token Missing.')
            while not args.oauth:
                args.oauth = input('  > ').strip()

        session.init(args.oauth)

        current_user = users.get_current_user()
        print((F"\n Welcome {current_user['display_name']} "
               F"(ID: {current_user['id']})\n"))

        if 'library' == args.command:
            do_library(args)
        elif 'playlist' == args.command:
            do_playlist(args)

        print('\n All done :)')

    except (KeyboardInterrupt, EOFError):
        print('\033[1;94m' + r"""

                 _____
                /  ___|
                \ `--.  ___  ___   _   _  ___  _   _   ___  ___   ___  _ __
                 `--. \/ _ \/ _ \ | | | |/ _ \| | | | / __|/ _ \ / _ \| '_ \
                /\__/ /  __/  __/ | |_| | (_) | |_| | \__ \ (_) | (_) | | | |
                \____/ \___|\___|  \__, |\___/ \__,_| |___/\___/ \___/|_| |_|
                                    __/ |
                                   |___/
        """ + '\033[0m')


if __name__ == '__main__':
    main()

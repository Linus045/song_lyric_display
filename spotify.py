import sys
import spotipy
import spotipy.util as util
import os


def getSong():
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    scope = 'user-library-read user-read-playback-state'
    token = util.prompt_for_user_token(username, scope)
    songName = ""
    songLength = 0
    songImgURl = None
    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.current_user_playing_track()
        if results != None:
            songName = results['item']['name']
            songLength = results['item']['duration_ms']
            songImgURl = results['item']['album']['images'][0]['url']
    else:
        print("Can't get token for", username)
    return songName, songLength, songImgURl


def getArtists():
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    scope = 'user-library-read user-read-playback-state'
    token = util.prompt_for_user_token(username, scope)
    songArtists = ""
    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.current_user_playing_track()
        if results:
            for num, artist in enumerate(results['item']['artists']):
                if num == len(results['item']['artists']) - 1:
                    songArtists += "{}".format(artist['name'])
                else:
                    songArtists += "{}, ".format(artist['name'])
    else:
        print("Can't get token for", username)
    return songArtists


def getFirstArtist():
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    scope = 'user-library-read user-read-playback-state'
    token = util.prompt_for_user_token(username, scope)
    songArtists = ""
    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.current_user_playing_track()
        if results:
            for num, artist in enumerate(results['item']['artists']):
                if num == 0:
                    songArtists += "{}".format(artist['name'])
                    break
    else:
        print("Can't get token for", username)
    return songArtists


def getCurrentSongInfo():
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    scope = 'user-library-read user-read-playback-state'
    token = util.prompt_for_user_token(username, scope)
    timestamp = 0
    progress_ms = 0
    isPlaying = None
    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.current_user_playing_track()
        if results:
            timestamp = results['timestamp']
            progress_ms = results['progress_ms']
            isPlaying = results['is_playing']
    else:
        print("Can't get token for", username)
    return timestamp, progress_ms, isPlaying

import sys
import spotipy
import spotipy.util as util
import os

scope = 'user-library-read user-read-playback-state user-modify-playback-state'
def getSong():
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
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
    token = util.prompt_for_user_token(username, scope)
    timestamp = 0
    progress_ms = 0
    device_info = None
    isPlaying = None
    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.current_playback()
        if results:
            timestamp = results['timestamp']
            progress_ms = results['progress_ms']
            isPlaying = results['is_playing']
            device_info = results['device']
    else:
        print("Can't get token for", username)
    return timestamp, progress_ms, isPlaying, device_info


def pauseOrResumeSong(device_id, is_playing):
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    token = util.prompt_for_user_token(username, scope)
    if token:
        sp = spotipy.Spotify(auth=token)
        try:
            if is_playing:
                result = sp.pause_playback(device_id)
            else:
                result = sp.start_playback(device_id)
        except:
            print("Can't pause song.")
    else:
        print("Can't get token for", username)

def nextOrPreviousSong(previousSong):
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    token = util.prompt_for_user_token(username, scope)
    if token:
        sp = spotipy.Spotify(auth=token)
        try:
            if previousSong:
                result = sp.previous_track()
            else:
                result = sp.next_track()
        except:
            print("Can't change song.", e)
    else:
        print("Can't get token for", username)

import sys
import spotipy
import spotipy.util as util
import os

scope = 'user-library-read user-read-playback-state user-modify-playback-state user-read-recently-played user-top-read'
def getSong():
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    token = util.prompt_for_user_token(username, scope)
    songName = ""
    songLength = 0
    songImgURl = None
    albumURI = ""
    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.current_user_playing_track()
        if results != None:
            if results['item']:
                songName = results['item']['name']
                songLength = results['item']['duration_ms']
                songImgURl = results['item']['album']['images'][0]['url']
                albumURI = results['item']['album']['id']
    else:
        print("Can't get token for", username)
    return songName, songLength, songImgURl, albumURI


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

def setCurrentVolume(volume, device_id = None):
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    token = util.prompt_for_user_token(username, scope)
    volume = max(0, min(round(volume), 100))
    if token:
        sp = spotipy.Spotify(auth=token)
        try:
            sp.volume(volume, device_id)
        except:
            print("Can't change volume.")
    else:
        print("Can't get token for", username)

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
            print("Can't change song.")
    else:
        print("Can't get token for", username)


def getAvailableDevices():
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    token = util.prompt_for_user_token(username, scope)
    devices = []
    if token:
        sp = spotipy.Spotify(auth=token)
        try:
            return sp.devices()['devices']
        except:
            print("Can't get devices.")
    else:
        print("Can't get token for", username)

def set_to_device(device):
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    token = util.prompt_for_user_token(username, scope)
    if token:
        sp = spotipy.Spotify(auth=token)
        try:
            sp.transfer_playback(device['id'])
        except:
            print("Can't connect to device.")
    else:
        print("Can't get token for", username)

def get_recently_played():
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    token = util.prompt_for_user_token(username, scope)
    recently_played_songs = None
    if token:
        sp = spotipy.Spotify(auth=token)
        try:
            recently_played_songs = sp.current_user_recently_played()
            if recently_played_songs['items']:
                return recently_played_songs['items']
        except:
            print("Error retrieving recently played songs.")
    else:
        print("Can't get token for", username)

def get_cover_url(track_id):
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    token = util.prompt_for_user_token(username, scope)
    songImgURl = None
    if token:
        sp = spotipy.Spotify(auth=token)
        try:
            track = sp.track(track_id)
            if track and track['album']:
                songImgURl = track['album']['images'][0]['url']
                return songImgURl
        except:
            print("Error retrieving track album cover image.")
    else:
        print("Can't get token for", username)

def get_top_list(time_range='medium_term'):
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    token = util.prompt_for_user_token(username, scope)
    if token:
        sp = spotipy.Spotify(auth=token)
        try:
            tracks = sp.current_user_top_tracks(time_range=time_range)
            if tracks['items']:
                return tracks['items']
        except:
            print("Error retrieving top list.")
    else:
        print("Can't get token for", username)

def queue_song(song_uri):
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    token = util.prompt_for_user_token(username, scope)
    if token:
        sp = spotipy.Spotify(auth=token)
        try:
            sp.add_to_queue(song_uri)
        except:
            print("Error queueing song.")
    else:
        print("Can't get token for", username)

def get_album(album_uri):
    username = os.getenv("SPOTIPY_ACCOUNT_NAME")
    token = util.prompt_for_user_token(username, scope)
    if token:
        sp = spotipy.Spotify(auth=token)
        try:
            album = sp.album(album_uri)
            return album
        except:
            print("Error retrieving album.")
    else:
        print("Can't get token for", username)

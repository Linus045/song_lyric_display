import os
import lyricsgenius


def getLyric(songname, artist):
    apiKey = os.getenv('GENIUS_ACCESS_TOKEN')
    genius = lyricsgenius.Genius(apiKey)
    song = genius.search_song(songname, artist, get_full_info=False)
    return song.lyrics

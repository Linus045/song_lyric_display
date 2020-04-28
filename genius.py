import os
import lyricsgenius


def getLyric(songname, artist):
    apiKey = os.getenv('GENIUS_ACCESS_TOKEN')
    genius = lyricsgenius.Genius(apiKey)
    try:
        song = genius.search_song(songname, artist, get_full_info=False)
        return song.lyrics
    except:
        return "No lyrics found..."

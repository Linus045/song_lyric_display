import os
import lyricsgenius


def getLyric(songname, artist):
    apiKey = os.getenv('GENIUS_ACCESS_TOKEN')
    genius = lyricsgenius.Genius(apiKey)
    try:
        bracketStart = songname.find("(")
        bracketEnd = songname.find(")")
        while (bracketStart != -1) and (bracketEnd != -1):
            songname = songname[:bracketStart] + songname[bracketEnd+1:]
            songname = songname.strip()
            bracketStart = songname.find("(")
            bracketEnd = songname.find(")")
        songname = songname.replace('  ', ' ')
        song = genius.search_song(songname, artist, get_full_info=False)
        return song.lyrics
    except:
        return "No lyrics found..."

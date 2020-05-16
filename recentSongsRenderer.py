import math
import pygame
import io
from urllib.request import urlopen
import spotify
class RecentSongsRenderer:

    def __init__(self, color_file, height, width, font):
        self.color_file = color_file
        self.height = height
        self.recently_played_songs = []
        self.boxes = {}
        self.boxWidth = 180
        self.font = font
        self.cover_urls_img_data = {}
        self.highlightedIdx = -1
        self.time = 0
        self.animate = True
        self.setWidth(width)

    def setWidth(self, width):
        self.width = width

    def drawBox(self, surface, pos, size, songname, artist, textPos, highlighted):
        text_song = self.font.render(songname, True, self.color_file.getColor('recentlyplayed.text.title'), None)
        text_artist = self.font.render(artist, True, self.color_file.getColor('recentlyplayed.text.artist'), None)

        rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        if highlighted:
            pygame.draw.rect(surface, self.color_file.getColor('recentlyplayed.highlighted'), rect)
        else:
            pygame.draw.rect(surface, self.color_file.getColor('recentlyplayed.background'), rect)
        surface.blit(text_song, (textPos[0] + 3,textPos[1]))
        surface.blit(text_artist, (textPos[0] + 3, textPos[1] + self.font.get_height() + 2))
        return rect

    def try_draw_cover_img(self, surface, pos, size, song_uri):
        coverImg = None
        if song_uri in self.cover_urls_img_data:
            coverImg = self.cover_urls_img_data[song_uri]
        else:
            albumCoverUrl = spotify.get_cover_url(song_uri)
            image_str = urlopen(albumCoverUrl).read()
            image_file = io.BytesIO(image_str)
            coverImg = pygame.image.load(image_file)
            coverImg = pygame.transform.scale(coverImg, size)
            if albumCoverUrl:
                self.cover_urls_img_data[song_uri] = coverImg
        if coverImg:
            surface.blit(coverImg, (pos[0] + 3,0))

    def checkMouseHit(self, mousePos):
        for key in self.boxes:
            box = self.boxes[key]
            if 'hitbox' in box:
                if box['hitbox'].collidepoint(mousePos):
                    self.animate = False
                    return box
        self.animate = True

    def boxClicked(self, box, mouseButton):
        if mouseButton == 1:
            spotify.queue_song(box['song_uri'])
            spotify.nextOrPreviousSong(False)
        elif mouseButton == 3:
            spotify.queue_song(box['song_uri'])

    def renderToSurface(self):
        surface = pygame.Surface((self.width, self.height))
        surface.set_colorkey(self.color_file.getColor('TRANSPARENT_KEY_COLOR'))
        if self.animate:
            self.time = self.time + 0.3

        if self.recently_played_songs:
            for songIdx in range(len(self.recently_played_songs)):
                if songIdx < len(self.recently_played_songs):
                    xOffset = (self.boxWidth + 5) * songIdx - (self.time % (len(self.recently_played_songs) * (self.boxWidth + 5) - self.width))
                    song = self.recently_played_songs[songIdx]
                    songname = ''
                    artists = []
                    song_uri = ''
                    if 'name' in song:
                        songname = song['name']
                        artists = song['artists']
                        song_uri = song['id']
                    elif 'track' in song:
                        songname = song['track']['name']
                        artists = song['track']['artists']
                        song_uri = song['track']['id']


                    artistsString = ''
                    for idx, artist in enumerate(artists):
                        artistsString = artistsString + artist['name']
                        if idx != len(artists) - 1:
                            artistsString = artistsString + ', '
                    img_padding = 3
                    img_height = self.height - img_padding
                    textPos =  (xOffset+ img_height + img_padding + 3, 0)
                    box = self.drawBox(surface, (xOffset,0),(self.boxWidth, self.height), songname, artistsString, textPos, self.highlightedIdx == songIdx)
                    self.try_draw_cover_img(surface, (xOffset + img_padding, img_padding), (img_height, img_height), song_uri)
                    self.boxes[songIdx] = {
                        'index':songIdx,
                        'hitbox':box,
                        'song_uri':song_uri,
                        'song_name':songname,
                        'artists':artists,
                        'artists_combined':artistsString
                    }
    

        return surface
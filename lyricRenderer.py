from pygame.locals import Rect
import pygame
LYRIC_COLOR = (255,255,255)
BACKGROUND_COLOR = (0,0,0)

class LyricRenderer():
    
    def __init__(self):
        self.lyrics_full = ""
        self.lyrics_surfaces = None
        self.width = 0
        self.height = 0
    
    def setFont(self, font):
        self.lyricFont = font

    def createSurfaces(self):
        lines = self.lyrics_full.split("\n")
        surfaces = []
        for line in lines:
            lineLength = self.lyricFont.size(line)[0]
            if lineLength > self.width:
                self.width = lineLength
            surfaces.append(self.lyricFont.render(line, True, LYRIC_COLOR))
        self.height = len(lines) * self.lyricFont.get_height()
        return surfaces

    def setLyric(self, lyrics):
        self.lyrics_full = lyrics
        self.lyrics_split = lyrics.split('\n')
        self.lyrics_surfaces = self.createSurfaces()

    def renderToSurface(self):
        surface = pygame.Surface((self.width, self.height))
        surface.set_colorkey(BACKGROUND_COLOR)
        for num, line in enumerate(self.lyrics_surfaces):
            rect = Rect(0, 0, *line.get_size())
            rect.top += num * self.lyricFont.get_height()
            surface.blit(line, rect)
        return surface

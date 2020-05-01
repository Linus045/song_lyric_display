from pygame.locals import Rect
import pygame
from colors import *

class LyricRenderer():
    
    def __init__(self):
        self.lyrics = None
        self.lyrics_surfaces = None
        self.width = 0
        self.height = 0
        self.maxWidth = 0

    def setFont(self, font):
        self.lyricFont = font

    #splits a sentence into multiple segments if it exceeds the maximal width
    def splitLine(self, line, newLines = None):
        if not newLines:
            newLines = []
        if self.lyricFont.size(line)[0] > self.maxWidth:
            oldWords = line.split()
            newLine = ''
            if len(oldWords) > 0:
                for wordIdx, word in enumerate(oldWords):
                    if (self.lyricFont.size(newLine + word)[0] < self.maxWidth):
                        if newLine == '':
                            newLine = word
                        else:
                            newLine += ' ' + word
                    else:
                        break
                newLines.append(newLine)
                self.splitLine(" ".join(oldWords[wordIdx:]), newLines)
        else:
            newLines.append(line)
        return newLines

    def makeLines(self, text):
        lines = []
        for line in text.split("\n"):
            for l in self.splitLine(line):
                lines.append(l)
        return lines

    def createSurfaces(self):
        if self.lyrics:
            self.lines = self.makeLines(self.lyrics)
            self.height = len(self.lines) * self.lyricFont.get_height()
            self.lyrics_surfaces = []
            for line in self.lines:
                lineLength = self.lyricFont.size(line)[0]
                if lineLength > self.width:
                    self.width = lineLength
                self.lyrics_surfaces.append(self.lyricFont.render(line, True, LYRICS_COLOR))
    
    def setLyric(self, lyrics):
        self.lyrics = lyrics
        self.createSurfaces()

    def setMaxWidth(self, maxWidth):
        self.maxWidth = max(maxWidth, 200)
        self.createSurfaces()

    def renderToSurface(self, bounds):
        surface = pygame.Surface((self.width, self.height))
        surface.set_colorkey(BLACK)
        for num, line in enumerate(self.lyrics_surfaces):
            rect = Rect(0, 0, *line.get_size())
            rect.top += num * self.lyricFont.get_height()
            if bounds.contains(rect):
                surface.blit(line, rect)
        return surface

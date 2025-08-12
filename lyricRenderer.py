from pygame.locals import Rect
import pygame

class LyricRenderer():
    
    def __init__(self, color_file):
        self.lyrics = None
        self.lyrics_surfaces = None
        self.color_file = color_file
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
            if len(oldWords) > 0:
                newLine = ''

                for wordIdx, word in enumerate(oldWords):
                    potentialNewLine = newLine + (' ' if newLine else '') + word
                    if (self.lyricFont.size(potentialNewLine)[0] < self.maxWidth):
                        newLine = potentialNewLine
                    else:
                        break

                if newLine == '':
                    # No words fit - append the first word and recurse on rest if any
                    newLines.append(oldWords[wordIdx])
                    rest = oldWords[wordIdx+1:]
                    if rest:
                        self.splitLine(" ".join(rest), newLines)
                else:
                    newLines.append(newLine)
                    rest = oldWords[wordIdx:]
                    if rest:
                        self.splitLine(" ".join(rest), newLines)
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
                self.lyrics_surfaces.append(self.lyricFont.render(line, True, self.color_file.getColor('player.lyrics')))
    
    def setLyric(self, lyrics):
        self.lyrics = lyrics
        self.createSurfaces()

    def setMaxWidth(self, maxWidth):
        self.maxWidth = max(maxWidth, 200)
        self.createSurfaces()

    def renderToSurface(self, bounds):
        surface = pygame.Surface((self.width, self.height))
        surface.set_colorkey(self.color_file.getColor('TRANSPARENT_KEY_COLOR'))
        for num, line in enumerate(self.lyrics_surfaces):
            rect = Rect(0, 0, *line.get_size())
            rect.top += num * self.lyricFont.get_height()
            if bounds.contains(rect):
                surface.blit(line, rect)
        return surface

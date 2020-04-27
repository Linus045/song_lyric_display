import pygame
import sys
import os
import spotipy
import spotipy.util as util
import time
from dotenv import *
from pygame.locals import *
from spotify import *
from genius import *

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (20, 100, 20)
BLUE = (0, 0, 255)
GREY = (30, 30, 30)
LIGHT_GREY = (50, 50, 50)

smallFont = None
basicFont = None


def renderMultilineString(text, font):
    lines = text.split("\n")
    labels = []
    for line in lines:
        labels.append(font.render(line, True, WHITE))
    return labels


def resizeScreen(newWidth, newHeight):
    global width, height, playingbarRect, windowSurface
    width = newWidth
    height = newHeight
    playingbarRect = Rect(2, 2, width - 4, 6)
    windowSurface = pygame.display.set_mode((width, height), pygame.RESIZABLE)


def main():
    global smallFont, basicFont, pygame, width, height, playingbarRect, windowSurface
    # load env variables
    load_dotenv('.env')

    # set up pygame
    pygame.init()

    # set up fonts
    fontFile = "fonts/RobotoMono-Medium.ttf"
    smallFont = pygame.font.Font(fontFile, 18)
    basicFont = pygame.font.Font(fontFile, 30)

    # set up the window
    width = 800
    height = 600
    # set window position
    #os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (width / 2, height / 2)
    windowSurface = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption('Spotify Lyric Screen')
    pygame.mouse.set_visible(False)
    resizeScreen(width, height)

    # set up the text
    textSong = basicFont.render("Unknown", True, WHITE, None)
    textSongRect = textSong.get_rect()
    textSongRect.top = 15
    textSongRect.left = 3

    textArtists = basicFont.render("Unknown", True, WHITE, None)
    textArtistsRect = textArtists.get_rect()
    textArtistsRect.top = textSongRect.bottom + 2
    textArtistsRect.left = 3

    textLyric = smallFont.render("LYRICS:", True, WHITE, None)
    textLyricRect = textLyric.get_rect()
    textLyricRect.top = textArtistsRect.bottom + 4
    textLyricRect.centerx = 800/2

    oldSongName = ""
    oldSongArtist = ""

    start = time.time()
    interval = 3
    nextCheck = start + 1

    # run the game loop
    lines = []
    startTime = 0
    timepassed_ms = 0
    isPlaying = False
    songLength = 300

    playingbarRect = Rect(2, 2, width - 4, 6)
    ratio = 0
    songActive = False

    timeSongStart = 0
    while True:
        # draw the white background onto the surface
        windowSurface.fill(GREY)

        if time.time() >= nextCheck:
            nextCheck += interval
            newSongName, songLength = getSong()
            if oldSongName != newSongName:
                oldSongName = newSongName
                songActive = True
                # TODO: request data in seperate thread so the program doesn't freeze
                textSong = basicFont.render(newSongName, True, WHITE, None)
                textArtists = basicFont.render(getArtists(), True, WHITE, None)
                lyrics = getLyric(newSongName, getFirstArtist())
                lines = renderMultilineString(lyrics, smallFont)
                print("[Updated] {}".format(newSongName))
                timeSongStart = time.time()

            startTime, timepassed_ms, isPlaying = getCurrentSongInfo()
        if songActive:
            # TODO: Set fixed framerate
            timeSince = time.time() - timeSongStart
            timepassed_ms += timeSince * 1000
            timeSongStart = time.time()
            # draw the text onto the surface
            windowSurface.blit(textSong, textSongRect)
            windowSurface.blit(textArtists, textArtistsRect)
            total_height = len(lines) * textLyricRect.height
            cur_line = round(len(lines) * ratio)
            for num, line in enumerate(lines):
                rect = Rect(textLyricRect.left - 150, textLyricRect.top,
                            textSong.get_rect().width, textLyricRect.height)
                rect.top += num * textLyricRect.height + height / 2 - total_height/1 * ratio
                if abs(num - cur_line) <= 2:
                    pygame.draw.rect(windowSurface, RED, rect)
                windowSurface.blit(line, rect)

            pygame.draw.rect(windowSurface, LIGHT_GREY, playingbarRect)
            ratio = timepassed_ms / songLength
            currentRect = Rect(playingbarRect.left, playingbarRect.top,
                               playingbarRect.width * ratio, playingbarRect.height)
            pygame.draw.rect(windowSurface, DARK_GREEN, currentRect)
            # draw the window onto the screen
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == 'ESC':
                    pygame.quit()
                    sys.exit(0)
            elif event.type == pygame.VIDEORESIZE:
                resizeScreen(event.w, event.h)


if __name__ == '__main__':
    main()

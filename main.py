import pygame
import sys
import os
import spotipy
import spotipy.util as util
import time
from dotenv import load_dotenv
from pygame.locals import color, Rect
import spotify
import genius
import lyricRenderer 
from colors import *
import win32gui
import win32con
import win32api

# whether or not the background should be transparent
showBackground = False

renderer = lyricRenderer.LyricRenderer()
smallFont = None
basicFont = None

def main():
    global smallFont, basicFont, pygame
    # load env variables
    load_dotenv('.env')

    # set up pygame
    pygame.display.init()
    pygame.font.init()

    # set up fonts
    fontFile = "fonts/RobotoMono-Medium.ttf"
    smallFont = pygame.font.Font(fontFile, 18)
    basicFont = pygame.font.Font(fontFile, 30)

    renderer.setFont(smallFont)

    # set up the window
    width = 800
    height = 600
    # set window position
    #os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (width / 2, height / 2)
    windowSurface = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    if not showBackground:
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*GREY), 0, win32con.LWA_COLORKEY)

    pygame.display.set_caption('Spotify Lyric Screen')
    pygame.mouse.set_visible(False)

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
            newSongName, songLength = spotify.getSong()

            if newSongName == "":
                textSong = basicFont.render("No song playing...", True, WHITE, None)
                print("[Updated] No song playing...")
            elif oldSongName != newSongName:
                oldSongName = newSongName
                songActive = True
                # TODO: request data in seperate thread so the program doesn't freeze
                textSong = basicFont.render(newSongName, True, WHITE, None)
                textArtists = basicFont.render(spotify.getArtists(), True, WHITE, None)
                lyrics = genius.getLyric(newSongName, spotify.getFirstArtist())
                renderer.setLyric(lyrics)
                print("[Updated] {}".format(newSongName))
                timeSongStart = time.time()

            startTime, timepassed_ms, isPlaying = spotify.getCurrentSongInfo()
        if songActive:
            # TODO: Set fixed framerate
            timeSince = time.time() - timeSongStart
            timepassed_ms += timeSince * 1000
            timeSongStart = time.time()
            # draw the text onto the surface
            windowSurface.blit(textSong, textSongRect)
            windowSurface.blit(textArtists, textArtistsRect)

            #generate the lyric surface and draw it 
            ratio = timepassed_ms / songLength
            lyricSurface = renderer.renderToSurface()
            windowSurface.blit(lyricSurface, (150, height / 2 - renderer.height/1 * ratio))
            pygame.draw.rect(windowSurface, LIGHT_GREY, playingbarRect)
            currentRect = Rect(playingbarRect.left, playingbarRect.top,
                               playingbarRect.width * ratio, playingbarRect.height)
            pygame.draw.rect(windowSurface, DARK_GREEN, currentRect)
            # draw the window onto the screen
        else:
            windowSurface.blit(textSong, textSongRect)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == 'ESC':
                    pygame.display.quit()
                    sys.exit(0)
            elif event.type == pygame.VIDEORESIZE:
                width = event.w
                height = event.h
                playingbarRect = Rect(2, 2, width - 4, 6)
                windowSurface = pygame.display.set_mode((width, height), pygame.RESIZABLE)


if __name__ == '__main__':
    main()

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
import urllib

# Whether or not the background should be transparent
showBackground = True
showFrame = True
startCentered = True
startPosition = (0, 0) # requires startCentered to be False
startSize = (800, 600)

renderer = lyricRenderer.LyricRenderer()
smallFont = None
basicFont = None

def createMainSurface(width, height):
    flags = pygame.HWACCEL
    if showFrame:
        flags = flags | pygame.RESIZABLE
    else:
        flags = flags | pygame.NOFRAME
    return pygame.display.set_mode((width, height), flags , 32)

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
    width = startSize[0]
    height = startSize[1]
    # set window positionsurfa
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (startPosition[0], startPosition[1])
    if startCentered:
        os.environ['SDL_VIDEO_CENTERED'] = "1"
    windowSurface = createMainSurface(width, height)
    # reset value so it doesn't get used when resizing the window later
    os.environ['SDL_VIDEO_WINDOW_POS'] = ""

    titlePos = (20,20)
    artistPos = (20,50)
    coverPos = (20,100)
    coverImgSize = (400,400)

    if not showBackground:
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*GREY), 0, win32con.LWA_COLORKEY)

    pygame.display.set_caption('Spotify Lyric Screen')
    pygame.mouse.set_visible(False)

    # set up the text
    textSong = None
    textArtists = None
    textLyric = None

    oldSongName = ""

    start = time.time()
    interval = 3
    nextCheck = start + 1

    # run the game loop
    startTime = 0
    timepassed_ms = 0
    isPlaying = False
    songLength = 300

    ratio = 0
    songActive = False
    coverImg = None

    timeSongStart = 0
    while True:
        # draw the white background onto the surface
        windowSurface.fill(GREY)

        if time.time() >= nextCheck:
            nextCheck += interval
            newSongName, songLength, songImgURl = spotify.getSong()

            if newSongName == "":
                songActive = False
                print("[Updated] No song playing...")
            elif oldSongName != newSongName:
                oldSongName = newSongName
                songActive = True
                # TODO: request data in seperate thread so the program doesn't freeze
                textSong = basicFont.render(newSongName, True, SONG_TITLE_COLOR, None)
                textArtists = basicFont.render(spotify.getArtists(), True, ARTIST_COLOR, None)
                lyrics = genius.getLyric(newSongName, spotify.getFirstArtist())
                renderer.setLyric(lyrics)
                if songImgURl:
                    urllib.request.urlretrieve(songImgURl, "coverImg.jpg")
                    coverImg = pygame.image.load('coverImg.jpg')
                    coverImg = pygame.transform.scale(coverImg, coverImgSize)
                print("[Updated] {}".format(newSongName))
                timeSongStart = time.time()

            startTime, timepassed_ms, isPlaying = spotify.getCurrentSongInfo()
        if songActive:
            # TODO: Set fixed framerate
            timeSince = time.time() - timeSongStart
            timepassed_ms += timeSince * 1000
            timeSongStart = time.time()
            # draw the text onto the surface
            windowSurface.blit(textSong, titlePos)
            windowSurface.blit(textArtists, artistPos)

            #generate the lyric surface and draw it 
            ratio = timepassed_ms / songLength
            lyricSurface = renderer.renderToSurface()
            windowSurface.blit(lyricSurface, (coverPos[0] + coverImgSize[0] + 20, height / 2 - renderer.height/1 * ratio))

            #draw the album cover image
            if coverImg:
                windowSurface.blit(coverImg, coverPos)

            #draw the progress bar
            playingbarRect = Rect(2, 2, width - 4, 6)
            pygame.draw.rect(windowSurface, PLAYING_BAR_BACKGROUNDCOLOR, playingbarRect)
            currentRect = Rect(playingbarRect.left, playingbarRect.top, playingbarRect.width * ratio, playingbarRect.height)
            pygame.draw.rect(windowSurface, PLAYING_BAR_COLOR, currentRect)
        else:
            textSong = basicFont.render("No song playing...", True, SONG_TITLE_COLOR, None)
            windowSurface.blit(textSong, titlePos)

        # update the window
        pygame.display.update()

        #handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.display.quit()
                    sys.exit(0)
            elif event.type == pygame.VIDEORESIZE:
                width = event.w
                height = event.h
                playingbarRect = Rect(2, 2, width - 4, 6)
                windowSurface = createMainSurface(width, height)


if __name__ == '__main__':
    main()

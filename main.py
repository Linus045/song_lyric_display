import pygame
import sys
import os
import time
from dotenv import load_dotenv
from pygame.locals import Rect
import spotify
import genius
import lyricRenderer 
import colors
import urllib
import pathlib
import json
import controlsRenderer
import sliderRenderer
import devices_renderer
import recentSongsRenderer

if sys.platform == 'win32':
    import win32gui
    import win32con
    import win32api

config = None
color_file = colors.Colors()
renderer = lyricRenderer.LyricRenderer(color_file)
smallFont = None
basicFont = None

filePath = pathlib.Path(__file__).parent.absolute()

def loadConfig():
    config = None
    path = filePath.joinpath('config.json')
    if path.exists():
        with path.open(mode='r') as settingsFile:
            config = json.load(settingsFile)
    else:
        print("No config.json exists. Creating a default one at ." + str(path))
        config = {
            "transparentBackground": False,
            "showFrame": True,
            "startCentered": True,
            "startPosition": {
                "x": 0,
                "y": 0,
            },
            "startSize": {
                "w":0,
                "h":0
            },
            "lyric_fontsize":18,
            "title_fontsize":30,
            "cover_image_size": {
                "w":400,
                "h":400
            },
            "show_mouse_cursor": False,
            "showOnTopSlider":'album'
        }
        with path.open(mode='w') as settingsFile:
            json.dump(config, settingsFile, indent=4)
    return config

def createMainSurface(width, height):
    flags = pygame.HWACCEL
    if config['showFrame']:
        flags = flags | pygame.RESIZABLE
    else:
        flags = flags | pygame.NOFRAME
    return pygame.display.set_mode((width, height), flags , 32)

def main():
    global smallFont, basicFont, pygame, config, color_file
    # load env variables
    load_dotenv(str(filePath.joinpath('.env')))
    config = loadConfig()
    color_file.loadColors(filePath)

    # set up pygame
    pygame.display.init()
    pygame.font.init()

    # set up fonts
    fontFile = str(filePath.joinpath('fonts/RobotoMono-Medium.ttf'))

    smallFont = pygame.font.Font(fontFile, config['lyric_fontsize'])
    basicFont = pygame.font.Font(fontFile, config['title_fontsize'])

    renderer.setFont(smallFont)

    displayInfo = pygame.display.Info()
    width, height = displayInfo.current_w, displayInfo.current_h
    # set up the window
    if config['startSize']['w'] > 0 and config['startSize']['h'] > 0:
        width = config['startSize']['w']
        height = config['startSize']['h']
    # set window positionsurfa
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (config['startPosition']['x'], config['startPosition']['y'])
    if config['startCentered']:
        os.environ['SDL_VIDEO_CENTERED'] = "1"
    windowSurface = createMainSurface(width, height)
    # reset value so it doesn't get used when resizing the window later
    os.environ['SDL_VIDEO_WINDOW_POS'] = ""
    os.environ['SDL_VIDEO_CENTERED'] = ''
    pygame.event.post(pygame.event.Event(pygame.VIDEORESIZE, {'w': width, 'h':height}))

    titlePos = (20,20)
    artistPos = (20,50)
    coverPos = (20,100)
    coverImgSize = (config['cover_image_size']['w'],config['cover_image_size']['h'])
    controlsPos = (20, coverPos[1] + coverImgSize[1] + 10)
    volumeSliderPos = (20, controlsPos[1] + 100 + 5)
    devicesSelectorPos = (20, volumeSliderPos[1] + 30)
    recentlyPlayedSongsPos = (0, 30) #x position will get calculated later

    controls_renderer = controlsRenderer.ControlsRenderer(color_file, coverImgSize[0])
    volume_slider_renderer = sliderRenderer.SliderRenderer(color_file, 0.5, coverImgSize[0])
    recent_songs_font = pygame.font.Font(fontFile, 14)
    recent_songs_renderer = recentSongsRenderer.RecentSongsRenderer(color_file, 50, width - coverImgSize[0], recent_songs_font)

    device_font = pygame.font.Font(fontFile, 14)
    device_selector_renderer = devices_renderer.DeviceSelectorRenderer(color_file,coverImgSize[0], height - devicesSelectorPos[1], device_font)

    if sys.platform == 'win32':
        if config['transparentBackground']:
            hwnd = pygame.display.get_wm_info()["window"]
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
            win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*color_file.getColor('BACKGROUND')), 0, win32con.LWA_COLORKEY)

    pygame.display.set_caption('Spotify Lyric Screen')
    pygame.mouse.set_visible(config['show_mouse_cursor'])

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
    device_info = None

    ratio = 0
    songActive = False
    coverImg = None

    timeSongStart = 0
    draggingVolumeSlider = False
    recently_played_songs = None
    albumURI = ""
    album = None
    while True:
        # draw the white background onto the surface
        windowSurface.fill(color_file.getColor('BACKGROUND'))
        controlsSurface = controls_renderer.renderToSurface()
        windowSurface.blit(controlsSurface, controlsPos)
        volumeSurface = volume_slider_renderer.renderToSurface()
        windowSurface.blit(volumeSurface, volumeSliderPos)
        deviceSelectorSurface = device_selector_renderer.renderToSurface(isPlaying)
        windowSurface.blit(deviceSelectorSurface, devicesSelectorPos)

        recentlyPlayedSongsSurface = recent_songs_renderer.renderToSurface()
        windowSurface.blit(recentlyPlayedSongsSurface, recentlyPlayedSongsPos)
        if time.time() >= nextCheck:
            nextCheck += interval
            newSongName, songLength, songImgURl, albumURI = spotify.getSong()

            if newSongName == "":
                songActive = False
                print("[Updated] No song playing...")
            elif oldSongName != newSongName:
                oldSongName = newSongName
                songActive = True
                # TODO: request data in seperate thread so the program doesn't freeze
                textSong = basicFont.render(newSongName, True, color_file.getColor('player.title'), None)
                textArtists = basicFont.render(spotify.getArtists(), True, color_file.getColor('player.artist'), None)
                lyrics = genius.getLyric(newSongName, spotify.getFirstArtist())
                renderer.setLyric(lyrics)
                if songImgURl:
                    imgPath = str(filePath.joinpath('coverImg.jpg'))
                    urllib.request.urlretrieve(songImgURl, imgPath)
                    coverImg = pygame.image.load(imgPath)
                    coverImg = pygame.transform.scale(coverImg, coverImgSize)
                print("[Updated] {}".format(newSongName))
                timeSongStart = time.time()
                if config['showOnTopSlider'] == 'album' and albumURI:
                    album = spotify.get_album(albumURI)
                    if album['album_type'] == 'single':
                        recently_played_songs = spotify.get_recently_played()
                    else:
                        recently_played_songs = album['tracks']['items']
                elif config['showOnTopSlider'] == 'top_tracks':
                    recently_played_songs = spotify.get_top_list()
                
                if recently_played_songs:
                    recent_songs_renderer.recently_played_songs = recently_played_songs
                recent_songs_renderer.time = 0

                labelWidth = max(titlePos[0] + textSong.get_width(), artistPos[0] + textArtists.get_width())
                xPos = max(coverPos[0] + coverImgSize[0] + 20, labelWidth)
                minWidth = width - xPos
                recent_songs_renderer.setWidth(minWidth)
                recentlyPlayedSongsPos = (xPos, recentlyPlayedSongsPos[1])
            devices = spotify.getAvailableDevices()
            if devices:
                device_selector_renderer.devices = devices

            startTime, timepassed_ms, isPlaying, device_info = spotify.getCurrentSongInfo()
            controls_renderer.songPlaying = isPlaying
            if device_info:
                current_volume = device_info['volume_percent']
                volume_slider_renderer.currentNormalized = current_volume/100
        if songActive:
            # TODO: Set fixed framerate
            timeSince = time.time() - timeSongStart
            if isPlaying:
                timepassed_ms += timeSince * 1000
            timeSongStart = time.time()
            # draw the text onto the surface
            windowSurface.blit(textSong, titlePos)
            windowSurface.blit(textArtists, artistPos)

            #generate the lyric surface and draw it 
            ratio = timepassed_ms / songLength
            heightOffset = height / 2 - renderer.height/1 * ratio
            lyricSurface = renderer.renderToSurface(Rect(0, artistPos[1] + basicFont.get_height() - heightOffset, renderer.width, height - 120))
            windowSurface.blit(lyricSurface, (coverPos[0] + coverImgSize[0] + 20, heightOffset))

            #draw the album cover image
            if coverImg:
                windowSurface.blit(coverImg, coverPos)

            #draw the progress bar
            playingbarRect = Rect(20, height-20, width - 40, 6)
            pygame.draw.rect(windowSurface, color_file.getColor('player.playingbar.background'), playingbarRect)
            currentRect = Rect(playingbarRect.left, playingbarRect.top, playingbarRect.width * ratio, playingbarRect.height)
            pygame.draw.rect(windowSurface, color_file.getColor('player.playingbar'), currentRect)
        else:
            textSong = basicFont.render("No song playing...", True, color_file.getColor('player.lyrics'), None)
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
                renderer.setMaxWidth(width - (coverPos[0] + coverImgSize[0] + 20 + 80))
            elif event.type == pygame.MOUSEMOTION:
                if draggingVolumeSlider:
                    volume_slider_renderer.update_value(mouse_pos[0])
                if songActive:
                    mouse_pos = (event.pos[0] - controlsPos[0], event.pos[1] - controlsPos[1]) 
                    controls_renderer.highlightPlaybutton = controls_renderer.playButtonRect.collidepoint(mouse_pos)
                    controls_renderer.highlightPreviousbutton = controls_renderer.previousButtonRect.collidepoint(mouse_pos)
                    controls_renderer.highlightNextbutton = controls_renderer.nextButtonRect.collidepoint(mouse_pos)

                    mouse_pos = (event.pos[0] - recentlyPlayedSongsPos[0], event.pos[1] - recentlyPlayedSongsPos[1])
                    highlightedBoxIndex = -1
                    hitBox = recent_songs_renderer.checkMouseHit(mouse_pos)
                    if hitBox:
                        if 'index' in hitBox:
                            highlightedBoxIndex = hitBox['index']
                    recent_songs_renderer.highlightedIdx = highlightedBoxIndex
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not draggingVolumeSlider:
                    mouse_pos = (event.pos[0] - volumeSliderPos[0], event.pos[1] - volumeSliderPos[1]) 
                    if volume_slider_renderer.borderRect.collidepoint(mouse_pos):
                        volume_slider_renderer.update_value(mouse_pos[0])
                        draggingVolumeSlider = True
                if not draggingVolumeSlider and songActive:
                    if device_info:
                        mouse_pos = (event.pos[0] - controlsPos[0], event.pos[1] - controlsPos[1]) 
                        if controls_renderer.playButtonRect.collidepoint(mouse_pos):
                            spotify.pauseOrResumeSong(device_info['id'], isPlaying)
                            isPlaying = not isPlaying
                            controls_renderer.songPlaying = isPlaying
                        elif controls_renderer.previousButtonRect.collidepoint(mouse_pos):
                            spotify.nextOrPreviousSong(True)
                        elif controls_renderer.nextButtonRect.collidepoint(mouse_pos):
                            spotify.nextOrPreviousSong(False)
            elif event.type == pygame.MOUSEBUTTONUP:
                if draggingVolumeSlider:
                    mouse_pos = (event.pos[0] - volumeSliderPos[0], event.pos[1] - volumeSliderPos[1])
                    volume = volume_slider_renderer.currentNormalized * 100
                    if device_info:
                        spotify.setCurrentVolume(volume, device_info['id'])
                    draggingVolumeSlider = False
                else:
                    mouse_pos = (event.pos[0] - devicesSelectorPos[0], event.pos[1] - devicesSelectorPos[1])
                    for device in device_selector_renderer.devices:
                        if 'hitbox' in device:
                            if device['hitbox'].collidepoint(mouse_pos):
                                spotify.set_to_device(device)

                    mouse_pos = (event.pos[0] - recentlyPlayedSongsPos[0], event.pos[1] - recentlyPlayedSongsPos[1])
                    clicked_box = recent_songs_renderer.checkMouseHit(mouse_pos)
                    if clicked_box:
                        recent_songs_renderer.boxClicked(clicked_box, event.button)

if __name__ == '__main__':
    main()

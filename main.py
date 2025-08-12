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
import threading

if sys.platform == 'win32':
    import win32gui
    import win32con
    import win32api

# target FPS
FPS = 60
clock = None

config = None
color_file = colors.Colors()
renderer = lyricRenderer.LyricRenderer(color_file)
smallFont = None
basicFont = None

filePath = pathlib.Path(__file__).parent.absolute()


class SongDataRequestThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        self.song_name = None
        self.song_artist = None
        self.lyrics = None
        self.result_ready = False
        # self.songImgURl = None
        self.spotify_artists = None
        self.coverImg = None
        self.songImgURl = None
        self.coverImgSize = None
        self.recently_played_songs = None
        self.isPlaying = None
        self.startTime = None
        self.timepassed_ms = None
        self.isPlaying = None
        self.device_info = None
        self.devices = None


    def set_lyrics_search_parameters(self, song_name, song_artists):
        with self.lock:
            self.song_name = song_name
            self.song_artist = song_artists

    def set_current_song(self, current_song, albumURI, songImgURl, coverImgSize):
        with self.lock:
            self.current_song = current_song
            self.albumURI = albumURI
            self.songImgURl = songImgURl
            self.coverImgSize = coverImgSize
    
    def run(self):
        song_name = None
        song_artist = None
        albumURI = None
        songImgURl = None
        coverImgSize = None

        with self.lock:
            songImgURl = self.songImgURl
            albumURI = self.albumURI
            coverImgSize = self.coverImgSize
            song_name = self.song_name
            song_artist = self.song_artist

        lyrics = genius.getLyric(song_name,song_artist)
        spotify_artists = spotify.getArtists()
        devices = spotify.getAvailableDevices()
        spotify_top_list = spotify.get_top_list()
        startTime, timepassed_ms, isPlaying, device_info = spotify.getCurrentSongInfo()

        album = None
        if config['showOnTopSlider'] == 'album' and albumURI:
            album = spotify.get_album(albumURI)

        if songImgURl:
            imgPath = str(filePath.joinpath('coverImg.jpg'))
            urllib.request.urlretrieve(songImgURl, imgPath)
            imgLoaded = pygame.transform.scale(pygame.image.load(imgPath), coverImgSize)

        with self.lock:
            self.coverImg = imgLoaded
            self.lyrics = lyrics
            self.spotify_artists = spotify_artists
            self.devices = devices

            if album:
                if album['album_type'] == 'single':
                    self.recently_played_songs = spotify.get_recently_played()
                else:
                    self.recently_played_songs = album['tracks']['items']
            elif config['showOnTopSlider'] == 'top_tracks':
                self.recently_played_songs = spotify_top_list

            self.startTime = startTime
            self.timepassed_ms = timepassed_ms
            self.isPlaying = isPlaying
            self.device_info = device_info

            self.result_ready = True
    
    def get_device_info(self):
        with self.lock:
            return self.device_info

    def get_coverImg(self):
        with self.lock:
            return self.coverImg

    def get_startTime(self):
        with self.lock:
            return self.startTime

    def get_isPlaying(self):
        with self.lock:
            return self.isPlaying
    
    def get_recently_played_songs(self):
        with self.lock:
            return self.recently_played_songs

    def get_spotify_artists(self):
        with self.lock:
            return self.spotify_artists

    def is_result_ready(self):
        with self.lock:
            return self.result_ready

    def get_lyrics(self):
        with self.lock:
            return self.lyrics

    def get_devices(self):
        with self.lock:
            return self.devices

    def get_timepassed_ms(self):
        with self.lock:
            return self.timepassed_ms




class SongChangedDetectorThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()

        self.song_active = False
        self.song_changed = False

        self.oldSongName = None
        self.newSongName = None
        self.song_duration_ms= None
        self.songImgURl = None
        self.albumURI = None
        self.running = True
        self.nextCheck = 10


    def run(self):
        while self.running:
            print("[API] Retrieving spotify current song...")
            newSongName, song_duration_ms, songImgURl, albumURI = spotify.getSong()

            with self.lock:
                self.newSongName = newSongName 
                self.song_duration_ms = song_duration_ms
                self.songImgURl = songImgURl
                self.albumURI = albumURI

                if self.newSongName == "":
                    self.song_active = False
                    print("[Updated] No song playing...")
                elif self.oldSongName != self.newSongName:
                    print("[Updated] New Song detected...")
                    self.oldSongName = self.newSongName
                    self.song_active = True
                    self.song_changed = True

            # release lock and wait for next check
            time.sleep(self.nextCheck)

    def set_detector_active(self):
        with self.lock:
            self.running = True

    def set_detector_offline(self):
        with self.lock:
            self.running = False

    def get_album_URI(self):
        with self.lock:
            return self.albumURI

    def get_songImg_URI(self):
        with self.lock:
            return self.songImgURl
        

    def is_song_active(self):
        with self.lock:
            return self.song_active
        
    def get_current_song(self):
        with self.lock:
            return self.newSongName


    def reset_song_changed(self):
        with self.lock:
            self.song_changed = False

    def has_song_changed(self):
        with self.lock:
            return self.song_changed
        
    def get_song_duration_ms(self):
        with self.lock:
            return self.song_duration_ms


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

    clock = pygame.time.Clock()

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

    # run the game loop
    startTime = 0
    isPlaying = False
    song_duration_ms = 0
    device_info = None

    ratio = 0
    timepassed_ms = 0

    timeSongStart = 0
    timeLastFrame = 0
    coverImg = None

    draggingVolumeSlider = False

    songDetectorThread = SongChangedDetectorThread()
    songDetectorThread.set_detector_active()
    songDetectorThread.start()
    
    songDataRequestThread = None
    refresh_interval = 10 # every 10 seconds see if something changed (e.g. skips in timeline)
    last_check = 0

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


        if (songDataRequestThread != None) and (songDataRequestThread.is_result_ready()):
            lyrics = songDataRequestThread.get_lyrics()
            artists = songDataRequestThread.get_spotify_artists()

            renderer.setLyric(lyrics)
            textSong = basicFont.render(current_song, True, color_file.getColor('player.title'), None)
            textArtists = basicFont.render(artists, True, color_file.getColor('player.artist'), None)
            coverImg = songDataRequestThread.get_coverImg()

            recently_played_songs = songDataRequestThread.get_recently_played_songs()
            if recently_played_songs:
                recent_songs_renderer.recently_played_songs = recently_played_songs
            recent_songs_renderer.time = 0

            song_duration_ms = songDetectorThread.get_song_duration_ms()

            labelWidth = max(titlePos[0] + textSong.get_width(), artistPos[0] + textArtists.get_width())
            xPos = max(coverPos[0] + coverImgSize[0] + 20, labelWidth)
            minWidth = width - xPos
            recent_songs_renderer.setWidth(minWidth)
            recentlyPlayedSongsPos = (xPos, recentlyPlayedSongsPos[1])

            devices = songDataRequestThread.get_devices()
            if devices:
                device_selector_renderer.devices = devices

            isPlaying = songDataRequestThread.get_isPlaying()
            controls_renderer.songPlaying = isPlaying
            device_info = songDataRequestThread.get_device_info()
            if device_info:
                current_volume = device_info['volume_percent']
                volume_slider_renderer.currentNormalized = current_volume/100

            new_timepassed_ms = songDataRequestThread.get_timepassed_ms()
            if abs(new_timepassed_ms - timepassed_ms) > 5000:
                print("timepassed_ms spotify:", new_timepassed_ms, " current timepassed:", timepassed_ms, " SYNCHING diff of: ", (new_timepassed_ms - timepassed_ms) / 1000, " seconds"  )
                timepassed_ms = new_timepassed_ms

            songDataRequestThread.join()
            songDataRequestThread = None

        # draw the text onto the surface
        if textSong:
            windowSurface.blit(textSong, titlePos)
        if textArtists:
            windowSurface.blit(textArtists, artistPos)

       

        current_song = songDetectorThread.get_current_song()
        albumURI = songDetectorThread.get_album_URI()
        songImgURI = songDetectorThread.get_songImg_URI()

        if current_song == "":
            print("[Updated] No song playing...")
            textSong = basicFont.render("No song playing...", True, color_file.getColor('player.lyrics'), None)
            windowSurface.blit(textSong, titlePos)
        elif songDetectorThread.has_song_changed():
            songDetectorThread.reset_song_changed()
   
            print("[Updated] {}".format(current_song))
            if albumURI and songImgURI:
                songDataRequestThread = SongDataRequestThread()
                songDataRequestThread.set_lyrics_search_parameters(current_song, spotify.getFirstArtist())
                songDataRequestThread.set_current_song(current_song, albumURI, songImgURI, coverImgSize)
                songDataRequestThread.start()
        elif time.time() > last_check + refresh_interval:
            last_check = time.time()
            if current_song and albumURI and songImgURI:
                songDataRequestThread = SongDataRequestThread()
                songDataRequestThread.set_lyrics_search_parameters(current_song, spotify.getFirstArtist())
                songDataRequestThread.set_current_song(current_song, albumURI, songImgURI, coverImgSize)
                songDataRequestThread.start()


        # TODO: Set fixed framerate
        timeNow = time.time()
        timeDelta = timeNow - timeLastFrame
        timeLastFrame = timeNow
        if isPlaying:
            timepassed_ms += timeDelta * 1000
        # print("timepassed_ms now: ", timepassed_ms)

        #generate the lyric surface and draw it
        ratio = 0
        if song_duration_ms:
            ratio = timepassed_ms / song_duration_ms
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

        # update the window
        pygame.display.update()

        #handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                songDetectorThread.set_detector_offline()
                songDetectorThread.join()

                if songDataRequestThread:
                    songDataRequestThread.join()

                pygame.display.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    songDetectorThread.set_detector_offline()
                    songDetectorThread.join()
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
                if songDetectorThread.is_song_active():
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
                if not draggingVolumeSlider and songDetectorThread.is_song_active():
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

        clock.tick(FPS)
if __name__ == '__main__':
    main()

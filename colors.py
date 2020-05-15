import pathlib
import json

class Colors():
    def __init__(self):
        self.colors = {}

    def loadColors(self, filePath):
        json_colors = None
        path = filePath.joinpath('colors.json')
        if path.exists():
            with path.open(mode='r') as color_file:
                json_colors = json.load(color_file)
        else:
            print("No colors.json exists. Creating a default one at ." + str(path))
            with path.open(mode='w') as color_file:
                json_colors = {
                    'BACKGROUND':[30, 30, 30],
                    'TRANSPARENT_KEY_COLOR':[0, 0, 0],
                    'player.title':[180, 180, 180],
                    'player.artist':[180, 180, 180],
                    'player.lyrics':[180, 180, 180],
                    'player.playingbar':[255, 120, 120],
                    'player.playingbar.background':[50, 50, 50],
                    'controls.playbutton.play':[20, 20, 20],
                    'controls.playbutton.play.background':[50, 50, 50],
                    'controls.playbutton.play.highlighted':[80, 80, 80],
                    'controls.playbutton.pause':[20, 20, 20],
                    'controls.playbutton.pause.background':[50, 50, 50],
                    'controls.playbutton.pause.highlighted':[80, 80, 80],
                    'controls.next':[20, 20, 20],
                    'controls.next.highlighted':[80, 80, 80],
                    'controls.previous':[20, 20, 20],
                    'controls.previous.highlighted':[80, 80, 80],
                    'controls.volume':[80, 80, 80],
                    'controls.volume.background':[20, 20, 20],
                    'devices.background':[50, 50, 50],
                    'devices.highlighted':[80, 80, 80],
                    'devices.soundbar':[255, 120, 120],
                    'devices.text':[20, 20, 20],
                }
                json.dump(json_colors, color_file, indent=4)
        for key in json_colors:
            color = json_colors[key]
            self.colors[key] = (color[0], color[1], color[2])

    def getColor(self, colorName):
        if colorName in self.colors:
            color = self.colors[colorName]
            return (color[0], color[1], color[2])
        else:
            raise Exception('Color not defined', colorName)

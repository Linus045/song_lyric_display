from pygame.locals import Rect
import pygame

class SliderRenderer:

    def __init__(self, color_file, currentNormalized, width):
        self.min = min
        self.max = max
        self.width = width
        self.color_file = color_file
        self.height = 15
        self.borderRect = None
        self.volumeRect = None
        self.currentNormalized = currentNormalized

    def update_value(self, x):
        self.currentNormalized = x / self.width

    def renderToSurface(self):
        surface = pygame.Surface((self.width, self.height))
        surface.set_colorkey(self.color_file.getColor('TRANSPARENT_KEY_COLOR'))
        self.borderRect = pygame.draw.rect(surface, self.color_file.getColor('controls.volume.background'), Rect(0, 0, self.width, self.height))
        self.volumeRect = pygame.draw.rect(surface, self.color_file.getColor('controls.volume'), Rect(0, 0, self.width * self.currentNormalized, self.height))
        return surface

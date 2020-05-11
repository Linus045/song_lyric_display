from pygame.locals import Rect
import pygame
from colors import *

class SliderRenderer:

    def __init__(self, currentNormalized, width):
        self.min = min
        self.max = max
        self.width = width
        self.height = 15
        self.borderRect = None
        self.volumeRect = None
        self.currentNormalized = currentNormalized

    def update_value(self, x):
        self.currentNormalized = x / self.width

    def renderToSurface(self):
        surface = pygame.Surface((self.width, self.height))
        surface.set_colorkey(BLACK)
        self.borderRect = pygame.draw.rect(surface, CONTROLS_COLOR, Rect(0, 0, self.width, self.height))
        self.volumeRect = pygame.draw.rect(surface, CONTROLS_COLOR_HIGHLIGHT, Rect(0, 0, self.width * self.currentNormalized, self.height))
        return surface

from pygame.locals import Rect
import pygame
from colors import *


class ControlsRenderer():

    def __init__(self, width):
        self.width = width
        self.height = 100
        self.left = (round(self.width/4 * 1), round(self.height/2))
        self.center = (round(self.width/4 * 2), round(self.height/2))
        self.right = (round(self.width/4 * 3), round(self.height/2))
        self.playbuttonRadius = self.height / 7.5
        self.nextButtonRect = None
        self.playButtonRect = None
        self.previousButtonRect = None
        self.highlightPlaybutton = False
        self.highlightPreviousbutton = False
        self.highlightNextbutton = False
        self.songPlaying = False


    def calculateTriangePoints(self):
        points = []
        xOffset = 4
        radius = self.playbuttonRadius
        points.append((self.center[0] + radius + xOffset, self.center[1]))
        points.append((self.center[0] - radius + xOffset, self.center[1] - radius))
        points.append((self.center[0] - radius + xOffset, self.center[1] + radius))
        return points

    def calculateArrowPoints(self, drawRight):
        points = []
        startPoint = self.left
        size = 6
        if drawRight:
            size = -size
            startPoint = self.right

        radius = self.height / -size
        points.append((startPoint[0], startPoint[1] + radius))
        points.append((startPoint[0], startPoint[1] - radius))
        points.append((startPoint[0] + radius, startPoint[1] - radius/2.5))
        points.append((startPoint[0] + radius, startPoint[1] - radius))
        points.append((startPoint[0] + radius + radius, startPoint[1]))
        points.append((startPoint[0] + radius, startPoint[1] + radius))
        points.append((startPoint[0] + radius, startPoint[1] + radius/2.5))

        return points

    def renderPolygon(self, surface, points, highlighted):
        button_color = CONTROLS_COLOR
        if highlighted:
            button_color = CONTROLS_COLOR_HIGHLIGHT
        return pygame.draw.polygon(surface, button_color, points)

    def renderPauseRect(self, surface, highlighted):
        button_color = CONTROLS_COLOR
        if highlighted:
            button_color = CONTROLS_COLOR_HIGHLIGHT
        radius = self.playbuttonRadius
        center = self.center
        yOffset = -5
        xOffset = -3
        leftTop = (center[0] - radius/2 + xOffset, center[1] - radius/2 + yOffset)
        pygame.draw.rect(surface, button_color, Rect(leftTop[0], leftTop[1], radius/2.5, radius * 2))

        leftTop = (center[0] + radius/2 + xOffset, center[1] - radius/2 + yOffset)
        pygame.draw.rect(surface, button_color, Rect(leftTop[0], leftTop[1], radius/2.5, radius * 2))


    def renderToSurface(self):
        surface = pygame.Surface((self.width, self.height))
        surface.set_colorkey(BLACK)

        self.playButtonRect = pygame.draw.circle(surface, CONTROLS_COLOR_BACKGROUND, self.center, round(self.height / 4))
        if self.songPlaying:
            self.renderPauseRect(surface, self.highlightPlaybutton)
        else:
            self.renderPolygon(surface, self.calculateTriangePoints(), self.highlightPlaybutton)

        self.previousButtonRect = self.renderPolygon(surface, self.calculateArrowPoints(False), self.highlightPreviousbutton)
        self.nextButtonRect = self.renderPolygon(surface, self.calculateArrowPoints(True), self.highlightNextbutton)
        return surface

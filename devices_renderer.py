import random
import pygame
from math import sin


class DeviceSelectorRenderer():

    def __init__(self,color_file, width, height, font):
        self.width = width
        self.height = height
        self.color_file = color_file
        self.boxHeight = 40
        self.devices = []
        self.font = font
        self.timer = 0

    def draw_playing_animation(self, surface, position, device):
        color = self.color_file.getColor('devices.soundbar')
        height = abs(sin(self.timer * 0.5) * (self.boxHeight - 30))
        box = pygame.Rect(position[0], position[1], 8, -height - (self.boxHeight/3))
        rect1 = pygame.draw.rect(surface, color, box)

        height = abs(sin(self.timer + 50) * (self.boxHeight - 30))
        box = pygame.Rect(position[0] + 9, position[1], 8, -height - (self.boxHeight/3))
        rect2 = pygame.draw.rect(surface, color, box)

        height = abs(sin(self.timer * 0.2) * (self.boxHeight - 30))
        box = pygame.Rect(position[0] + 18, position[1], 8, -height - (self.boxHeight/3))
        rect3 = pygame.draw.rect(surface, color, box)


    def draw_box(self, surface, position, device):
        box = pygame.Rect(position[0], position[1],self.width,self.boxHeight)
        color = self.color_file.getColor('devices.background')
        if device['is_active']:
            color = self.color_file.getColor('devices.highlighted')

        rect = pygame.draw.rect(surface, color, box)

        text = self.font.render(device['name'], True, self.color_file.getColor('devices.text'), None)
        surface.blit(text, (box.left + 3, box.top))

        return rect

    def renderToSurface(self, is_playing):
        surface = pygame.Surface((self.width, self.height))
        surface.set_colorkey(self.color_file.getColor('TRANSPARENT_KEY_COLOR'))
        box = pygame.Rect(0, 0,self.width, self.height)
        rect = pygame.draw.rect(surface, self.color_file.getColor('BACKGROUND'), box)
        self.timer = self.timer + 60/1000 + random.random()/1000

        for idx, device in enumerate(self.devices):
            pos = (0, idx * (self.boxHeight + 3))
            hitbox = self.draw_box(surface, pos, device)
            self.devices[idx]['hitbox'] = hitbox
            if device['is_active'] and is_playing:
                self.draw_playing_animation(surface, (hitbox.width - 60, pos[1] + hitbox.height - 10 ), device)
        return surface

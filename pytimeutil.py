#This module REQUIRES Pygame to work! Please import it beforehand!
import pygame, sys
from pygame.locals import *
clock = pygame.time.Clock()
class Timer:
    def __init__(self, framerate):
        self.clock = pygame.time.Clock()
        self.timescale = 1
        self.real_fps = 0
        self.totalfps = 0
        self.framecount = 0
        self.avg_fps = 0
        self.fpscount = 0
        self.frametime = 0
        self.framerate = framerate
        self.framedivisor = 0
        self.framebuffer = -1

    def adv(self): #Updates clock every frame; adv stands for "advance"
        self.framecount += 1
        self.real_fps = round(self.clock.get_fps(),1)
        self.totalfps += self.real_fps

        if self.fpscount >= self.framebuffer and self.framebuffer != 10:
            self.fpscount = 0
            self.totalfps = 0
            
        if clock.get_fps() != 0:
            self.totalfps += clock.get_fps() 
            self.fpscount += 1 #Only counts averages if nonzero framerate
            self.avgfps = self.totalfps / self.fpscount
            self.framedivisor = self.avgfps
        
        else:
            self.framedivisor = self.framerate
            
        self.frametime = (self.framecount * 1000 / self.framedivisor) * 0.001 * self.timescale

    def give(self): #Quite literally "gives" time
        return self.frametime


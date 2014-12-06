import pygame, sys
from pygame.locals import *
import math
import pytimeutil
import random

class MySprite(pygame.sprite.Sprite):
    def __init__(self, target):
        pygame.sprite.Sprite.__init__(self) #extend the base Sprite class
        self.master_image = None
        self.frame = 0
        self.old_frame = -1
        self.frame_width = 1
        self.frame_height = 1
        self.first_frame = 0
        self.last_frame = 0
        self.columns = 1
        self.last_time = 0

    #X property
    def _getx(self): return self.rect.x
    def _setx(self,value): self.rect.x = value
    X = property(_getx,_setx)

    #Y property
    def _gety(self): return self.rect.y
    def _sety(self,value): self.rect.y = value
    Y = property(_gety,_sety)

    #position property
    def _getpos(self): return self.rect.topleft
    def _setpos(self,pos): self.rect.topleft = pos
    position = property(_getpos,_setpos)
        

    def load(self, filename, width, height, columns):
        self.master_image = pygame.image.load(filename).convert_alpha()
        self.frame_width = width
        self.frame_height = height
        self.rect = Rect(0,0,width,height)
        self.columns = columns
        #try to auto-calculate total frames
        rect = self.master_image.get_rect()
        self.last_frame = (rect.width // width) * (rect.height // height) - 1

    def update(self, current_time, rate):
        #update animation frame number
        if current_time > self.last_time + rate:
            self.frame += 1
            if self.frame > self.last_frame:
                self.frame = self.first_frame
            self.last_time = current_time

        #build current frame only if it changed
        if self.frame != self.old_frame:
            frame_x = (self.frame % self.columns) * self.frame_width
            frame_y = (self.frame // self.columns) * self.frame_height
            rect = Rect(frame_x, frame_y, self.frame_width, self.frame_height)
            self.image = self.master_image.subsurface(rect)
            self.old_frame = self.frame

    def __str__(self):
        return str(self.frame) + "," + str(self.first_frame) + \
               "," + str(self.last_frame) + "," + str(self.frame_width) + \
               "," + str(self.frame_height) + "," + str(self.columns) + \
               "," + str(self.rect)
    
class Level:
    def __init__(self, surface):

        self.surf = surface
        pygame.init()
        self.resX = 800
        self.resY = 700
        self.clock = pygame.time.Clock()

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GRAY = (128, 128, 128)

        self.jumping = True
        self.alive = True
        self.pos = (0, 0)
        self.vel = (0, 0)
        self.velvect = (0, 0)
        self.grav = (0, -1.5)
        self.acc = self.grav
        self.objlist = []

        self.objlist.append((0, self.resY - 25, 9999, 9999, 'plt'))
        self.objlist.append((400, self.resY - 200, 200, 25, 'plt'))

        self.objlist.append((1000, self.resY - 600, 200, 25, 'plt'))
        #self.objlist.append((800, 300, 200, 25, 'plt'))

        self.objlist.append((801, self.resY - 400, 200, 1000, 'kill'))
        
        self.objlist.append((1500, self.resY - 75, 50, 50, 'chk', False)) #Coordinates of a checkpoint, and whether or not it's been passed already.
        
        self.objlist.append((2000, self.resY - 75, 50, 50, 'chk', False)) #Coordinates of a checkpoint, and whether or not it's been passed already.

        self.kickback = 12 #How far the self.player jumps back after being self.hit by an obstacle

        ##Item Definitions: plt = platform, kill = kills self.player when collided with

        self.playerSprite = MySprite(self.surf)
        self.playerSprite.load("FlippySpriteSheetLarge.png", 50, 50, 5)
        self.playerSprite.first_frame = 0
        self.playerSprite.last_frame = 4
        self.playerGroup = pygame.sprite.Group()
        self.playerGroup.add(self.playerSprite)

        self.spritepalette = {'DEAD': (0),
                         'HIT-R': (5),
                         'HIT-L': (10),
                         'JUMPING': (15),
                         'FALLING': (20),
                         'CROUCH-R': (25),
                         'CROUCH-L': (30),
                         'RUNNING-R': (35, 39),
                         'RUNNING-L': (40, 44),
                         'DEC-R': (45, 49),
                         'DEC-L': (50, 54),
                         'PUSH-R': (55, 59),
                         'PUSH-L': (60, 64),
                         'ST-R': (65, 69),
                         'ST-L': (70, 74),}

        
        self.timewarp = .75
        
        self.camera = (0, 0)
        self.movecameraX = 0
        self.movecameraY = 0
        self.trackspeedX = 10
        self.trackspeedY = 10
        self.track_sensitivityX = 15
        self.track_sensitivityY = 25
        
        self.camshakemaxX = 10 #The maximum amount of camera shake in the X direction
        self.camshakemaxY = 10 #The maximum amount of camera shake in the Y direction
        self.earthquake = False #Does the camera need to shake yet?
        self.shakestep = 0 #What step the camera is in a shaking procedure (moving forward, moving back, moving back to home position?)
        self.startedshaking = 0 #Time at which shaking started--timing purposes
        
        
        self.camshakeX = 0 #The camera's current position when shaking
        self.camshakeY = 0


        
        self.manualcam = True

        self.respawning = True
        self.trans = -self.resY#Transition counter for death animation
        self.curtainrect = pygame.Rect(0, self.trans, self.resX, self.resY*2)
        self.titlerect = pygame.Rect(0, 0, 0, 0)
        self.titlerect.right = self.resX + 100
        self.cancollide = True #If collisions will affect character
        self.maxhealth = 3
        self.health = self.maxhealth
        self.hit = False
        self.vulnerable = True
        self.neverleft = False #If you self.hit an obstacle and you don't leave, the counter still goes down.
        self.whenhit = 0
        self.spawnAt = (0, 0)

        self.lvl_name = 'Level -1: Test Level'

        self.frict = 0.8

        self.myFont = pygame.font.Font(None, 25)
        self.charheight = self.myFont.size('A')[1] + 3 #This is just a character to test for text height plus a little padding in between.
        self.titleFont = pygame.font.Font(None, 100)
        self.titletext = self.titleFont.render('BLAGOBLAGOBLAG!', 1, self.WHITE)


        self.direction = 0 #-1 = left, 1 = right, 0 = stop
        self.lastmoved = 1# 1= right, -1 = left

        self.dbg_mode = True

        self.collidingwith = 0
        self.state = None
        self.crouching = False
        self.playerwidth = 50
        self.playerheight = 50
        self.crouchingheight = 15
        self.player = pygame.Rect(self.pos[0] - self.camera[0], self.pos[1] - self.camera[1], self.playerwidth, self.playerheight) 

        self.gametime = pytimeutil.Timer(60)
        self.ticks = pygame.time.get_ticks()

    def run(self):
        
        
        self.surf.fill(self.WHITE)
        mouse = pygame.mouse.get_pos()

	########################################################################################################################################################################################
        #Movement and Animation
        ########################################################################################################################################################################################



        
                
        if not self.alive: #If self.player has died, nothing moves.
            self.direction = 0
            self.movecameraX = 0
            self.movecameraY = 0


            
        if self.jumping: #If the self.player is self.jumping, only gravity affects velocity. Otherwise, both gravity and self.player movement affect velocity.
            self.acc = (self.grav[0]*self.timewarp, self.grav[1]*self.timewarp**2)
        elif not self.jumping:
            self.acc = ((self.grav[0] + (self.direction*3))*self.timewarp, self.grav[1]*self.timewarp**2)

        
        self.vel = (self.vel[0] + self.acc[0], self.vel[1] - self.acc[1]) #Updates velocity and Acceleration
        
        self.pos = (self.pos[0] + self.vel[0], self.pos[1] + self.vel[1])
        


        if pygame.mouse.get_pressed() == (1, 0, 0) and self.dbg_mode:
            self.pos = (mouse[0] + self.camera[0], mouse[1] + self.camera[1])
            self.vel = (0, 0)

        if pygame.mouse.get_pressed() == (0, 0, 1):
            self.earthquake = True
            
        if not self.manualcam:
            if self.player.centerx > (self.resX/2) + self.track_sensitivityX: #Tracks self.camera to self.player's X coordinate until it centers. Then, it stops the self.camera.
                self.movecameraX = 1
                
            elif self.player.centerx < (self.resX/2) - self.track_sensitivityX:
                self.movecameraX = -1

            else:
                self.movecameraX = 0
                
            self.trackspeedX = (abs(self.player.centerx - (self.resX/2)) - self.track_sensitivityX) / 10

            if self.player.centery > (self.resY/2) + self.track_sensitivityY: #Tracks self.camera to self.player's Y coordinate until it centers. Then, it stops the self.camera.
                self.movecameraY = 1
                
            elif self.player.centery < (self.resY/2) - self.track_sensitivityY:
                self.movecameraY = -1

            else:
                self.movecameraY = 0
                
            self.trackspeedY = (abs(self.player.centery - (self.resY/2)) + self.track_sensitivityY) / 15

        if self.dbg_mode:
            pygame.draw.rect(self.surf, self.BLUE, (self.resX/2 - self.track_sensitivityX - self.player.w, self.resY/2 - self.track_sensitivityY - self.player.h/2, self.track_sensitivityX*2 + self.player.w*2, self.track_sensitivityY*2 + self.player.h), 3)
            
        self.camera = (self.camera[0] + self.trackspeedX*self.movecameraX*self.timewarp, self.camera[1] + self.trackspeedY*self.movecameraY*self.timewarp)

        if self.camera[0] <= 0:
            self.camera = (0, self.camera[1])

        if self.camera[1] >= 0:
            self.camera = (self.camera[0], 0)



        ########################################################################################################################################################################################
        #Camera Shaking "gizmo"
        ########################################################################################################################################################################################



        if self.earthquake and self.shakestep == 0:
            self.earthquake = False
            self.startedshaking = self.gametime.give() #Gets time when shaking was called to start
            self.shakestep = 1

        if self.shakestep == 1 or (self.shakestep == 3 and abs(self.gametime.give() - self.startedshaking) >= 0.02):
            self.camshakeX = self.camshakemaxX * ((random.randint(0, 1) * 2) - 1) #RNG either gives out a 1 or -1; causes the camera shake to either be positive or negative
            self.camshakeY = self.camshakemaxY * ((random.randint(0, 1) * 2) - 1)
            self.shakestep += 1
            
        if self.shakestep == 2 and abs(self.gametime.give() - self.startedshaking) >= 0.01 or (self.shakestep == 4 and abs(self.gametime.give() - self.startedshaking) >= 0.03):
            self.camshakeX = 0
            self.camshakeY = 0
            if self.shakestep == 2:
                self.shakestep += 1
            elif self.shakestep == 4:
                self.shakestep = 0


        self.camera = (self.camera[0] + self.camshakeX, self.camera[1] + self.camshakeY)

        ########################################################################################################################################################################################
        #Death and Respawning Animation
        ########################################################################################################################################################################################
        if self.pos[1] > self.resX + 200:
            self.alive = False

        if not self.alive: #Resets level to beginning
            if self.trans >= -self.resY and self.trans < -self.resY + 50:
                self.pos = (self.spawnAt[0], self.spawnAt[1] - 100)
                self.player.topleft = (0, 0)
                self.camera = (0, 0)
                self.movecameraX = 0
                self.movecameraY = 0
                self.vel = (0, 0)
                self.acc = self.grav
                self.cancollide = True
                #print("PLACING PLAYER")
            self.respawning = True

        if self.respawning:
            self.curtainrect = Rect(0, self.trans, self.resX, self.resY * 2)
            self.titlerect = self.titletext.get_rect()
            self.titlerect.centerx = self.curtainrect.centerx
            
            if self.trans < 0:
                self.titlerect.centery = self.curtainrect.bottom - (self.resY / 2)

            if self.curtainrect.bottom > self.resY and self.curtainrect.top < 0:
                self.titlerect.centery = self.resY / 2

            if self.curtainrect.top >= 0:
                self.titlerect.centery = self.curtainrect.top + (self.resY / 2)
                
            if self.trans < self.resY * 2:
                self.trans += 10 #Starts self.transition for dying animation
                #print("MOVING CURTAIN")
                self.health = self.maxhealth

            if self.trans == self.resY:
                self.alive = True
                #print("READY TO GO")
          
            if self.trans >= self.resY * 2: #If "curtain" reaches bottom of screen and is no longer visible, raise it back up to default position and mark animation ('self.respawning') as finished.
                 self.trans = -self.resY * 2
                 self.respawning = False
                 #print("RESET CURTAIN")





        
        if self.crouching:
            self.player.height = self.crouchingheight
        else:
            self.player.height = self.playerheight

        self.player.topleft = (self.pos[0] - self.camera[0], self.pos[1] - self.camera[1]) #self.positions and draws self.player
        pygame.draw.rect(self.surf, self.RED, self.player, 0)
        self.playerSprite.position = self.player.topleft
        self.playerGroup.update(self.ticks, 100)
        self.playerGroup.draw(self.surf)

        ########################################################################################################################################################################################
        #Draws Platforms and tests collisions between platforms and self.player
        ########################################################################################################################################################################################
            
        self.collidingwith = 0 #How many objects are colliding with self.player
        visibleobjects = 0
        leftbound = 0
        rightbound = self.resX
        topbound = 0
        bottombound = self.resY
        if self.dbg_mode:
            pygame.draw.rect(self.surf, (0, 255, 0), (leftbound, topbound, rightbound-leftbound, bottombound-topbound), 3)
        for num in range(0, len(self.objlist)):
            obj = self.objlist[num]
            visible = False #Boolean for whether or not objects are drawn if they are within the boundaries
            if ((((obj[0] - self.camera[0]) >=  leftbound and (obj[0] - self.camera[0]) <= rightbound) or
                ((obj[0] - self.camera[0] + obj[2]) >= leftbound and (obj[0] - self.camera[0] + obj[2]) <= rightbound) or
                ((obj[0] - self.camera[0]) <= leftbound and (obj[0] - self.camera[0] + obj[2]) >= rightbound)) and
                (((obj[1] - self.camera[1]) >= topbound and (obj[1] - self.camera[1]) <= bottombound) or
                ((obj[1] - self.camera[1] + obj[3]) >= topbound and (obj[1] - self.camera[1] + obj[3]) <= bottombound) or
                ((obj[1] - self.camera[1]) <= topbound and (obj[1] - self.camera[1] + obj[3]) >= bottombound))): #Clipping: doesn't load objects if they are off the left or right edge of the screen. Excludes objects above or below the screen, since the self.camera sometimes can't keep up with vertical motion.
                visibleobjects += 1
                visible = True
    #Collision with platform ########################################################################################################################################################################################
            if obj[4] == 'plt':
                platform = pygame.Rect(obj[0] - self.camera[0], obj[1] - self.camera[1], obj[2], obj[3])
                if visible:
                    pygame.draw.rect(self.surf, self.GRAY, platform, 0)

                if self.player.right > platform.left and self.player.left < platform.right and self.cancollide:                    #if self.player.top > platform.centery and self.player.top <= platform.bottom:
                        #print("CEILING")
                    if (self.player.bottom >= platform.top and self.player.top <= platform.top) or (self.vel[1] + self.player.bottom > platform.top and self.vel[1] >= 0 and self.player.bottom <= platform.top): #Floor Collision; also looks ahead a frame to keep self.players from falling through thin platforms.
                        self.player.bottom = platform.top
                        self.pos = (self.pos[0], self.player.top + self.camera[1])
                        self.vel = (self.vel[0] * self.frict, 0)
                        self.jumping = False
                        self.hit = False
                        self.collidingwith += 1
                        
                    if self.player.top <= platform.bottom and self.player.bottom > platform.bottom: #Ceiling collision
                        self.player.top = platform.bottom
                        self.pos = (self.pos[0], 1 + self.player.top + self.camera[1])
                        self.vel = (self.vel[0], 0)
                        self.hit = False
                        self.collidingwith += 1

                if self.player.top > platform.top and self.player.bottom < platform.bottom and self.cancollide:#Right collision
                    if self.player.left <= platform.right and self.player.left > platform.centerx:
                        self.player.left = platform.right
                        self.pos = (self.player.left + self.camera[0], self.pos[1])
                        self.vel = (0, self.vel[1])
                        self.hit = False

                    if self.player.right >= platform.left and self.player.right <= platform.centerx: #Left collision
                        self.player.right = platform.left
                        self.pos = (self.player.left + self.camera[0], self.pos[1])
                        self.vel = (0, self.vel[1])
                        self.hit = False
                        
                self.jumping = self.collidingwith == 0
                
    #Passing a Checkpoint ########################################################################################################################################################################################
            if obj[4] == 'chk':
                checkpoint = pygame.Rect(obj[0] - self.camera[0], obj[1] - self.camera[1], obj[2], obj[3])
                if visible:
                    if obj[5]:#Activated chekckpoint
                        pygame.draw.rect(self.surf, (0, 255, 0), checkpoint, 0)
                        if obj[0] > self.spawnAt[0]:
                            self.spawnAt = (obj[0], obj[1])
                    elif not obj[5]:#inactive checkpoint
                        pygame.draw.rect(self.surf, (0, 128, 0), checkpoint, 0)

                if checkpoint.colliderect(self.player):
                    temp = list(self.objlist[num])
                    temp[5] = True
                    self.objlist[num] = tuple(temp)
            
    #Collision with dangerous obstacle (i.e. spikes, freezing-cold water, etc... ########################################################################################################################################################################################
            if obj[4] == 'kill':
                kill = pygame.Rect(obj[0] - self.camera[0], obj[1] - self.camera[1], obj[2], obj[3])
                if visible:
                    pygame.draw.rect(self.surf, (255, 128, 0), kill, 0)
                if self.player.right > kill.left and self.player.left < kill.right and self.cancollide: #Floor Collision
                    if (self.player.bottom >= kill.top and self.player.top <= kill.top) or (self.vel[1] + self.player.bottom > kill.top and self.vel[1] >= 0 and self.player.bottom <= kill.top):
                        self.player.bottom = kill.top
                        self.pos = (self.pos[0], self.player.top + self.camera[1])
                        self.jumping = False
                        if self.vulnerable:
                            self.vel = (-self.kickback * self.timewarp * self.lastmoved, -self.kickback * self.timewarp)
                            self.health -= 1
                            self.hit = True
                        else:
                            self.vel = (self.vel[0] * self.frict * self.timewarp, 0)
                            self.hit = False
                        
                        if not self.neverleft:
                            self.whenhit = self.gametime.give()
                        self.neverleft = True
                        self.vulnerable = False
                    if self.player.top <= kill.bottom and self.player.bottom > kill.bottom:#Ceiling collision
                        self.player.top = kill.bottom
                        self.pos = (self.pos[0], self.player.top + self.camera[1] + 1)
                        self.jumping = False
                        if self.vulnerable:
                            self.vel = (self.vel[0] * self.frict * self.timewarp, 0)
                            self.health -= 1
                            self.hit = True
                        else:
                            self.vel = (self.vel[0] * self.frict * self.timewarp, 0)
                            self.hit = False
                        
                        if not self.neverleft:
                            self.whenhit = self.gametime.give()
                        self.neverleft = True
                        self.vulnerable = False
                if self.player.bottom > kill.top and self.player.top < kill.bottom and self.cancollide:#Right-side collision
                    if self.player.left <= kill.right and self.player.left >= kill.centerx:
                        self.player.left = kill.right
                        self.pos = (self.player.left + self.camera[0], self.pos[1])
                        if self.vulnerable:
                            self.vel = (-self.kickback * self.timewarp * self.lastmoved, -self.kickback * self.timewarp)
                            self.health -= 1
                            self.hit = True
                        else:
                            self.vel = (0, self.vel[1])
                            self.hit = False
                        
                        if not self.neverleft:
                            self.whenhit = self.gametime.give()
                        self.neverleft = True
                        self.vulnerable = False   
                    if self.player.right >= kill.left and self.player.right < kill.centerx:#Left-side collision
                        self.player.right = kill.left
                        self.pos = (self.player.left + self.camera[0], self.pos[1])
                        if self.vulnerable:
                            self.vel = (-self.kickback * self.timewarp * self.lastmoved, (-self.kickback * self.timewarp))
                            self.health -= 1
                            self.hit = True
                        else:
                            self.vel = (0, self.vel[1])
                            self.hit = False
                            
                        if not self.neverleft:
                            self.whenhit = self.gametime.give()
                        self.neverleft = True
                        self.vulnerable = False                                            
                if self.health < 0:
                    self.cancollide = False

        
                

        ########################################################################################################################################################################################
        #Nulls out velocity if less than a certain amount.
        ########################################################################################################################################################################################


        self.vel = (round(self.vel[0], 2), round(self.vel[1], 2))
        self.pos = (round(self.pos[0], 2), round(self.pos[1], 2))
        
        if abs(self.vel[0]) < 0.1:
            self.vel = (0, self.vel[1])
            
        if abs(self.vel[1]) < 0.1:
            self.vel = (self.vel[0], 0)

        self.velvect = (round(math.sqrt(self.vel[0]**2 + self.vel[1]**2), 2), round(math.degrees(math.atan2(self.vel[1],self.vel[0])), 2))




        ########################################################################################################################################################################################
        #State Machine Logic
        ########################################################################################################################################################################################

        if not self.cancollide:
            self.state = 'DEAD'
        elif self.hit:
            if self.lastmoved == -1:
                self.state = 'HIT-L'
            elif self.lastmoved == 1:
                self.state = 'HIT-R'
        elif self.jumping:
            if (self.vel[1] >= 0 and self.acc[1] > 0) or (self.vel[1] <= 0 and self.acc[1] < 0): #If the character is moving vertically against the force of acceleration, it is self.jumping.
                self.state = 'JUMPING'
            elif (self.vel[1] < 0 and self.acc[1] < 0) or (self.vel[1] > 0 and self.acc[1] < 0): #Otherwise, it is falling.
                self.state = 'FALLING'
        elif self.crouching:
            if self.lastmoved == -1:
                self.state = 'CROUCH-L'
            elif self.lastmoved == 1:
                self.state = 'CROUCH-R'
        elif self.acc[0] > 0 and self.vel[0] > 0:
            self.state = 'RUNNING-R'
        elif self.acc[0] < 0 and self.vel[0] < 0:
            self.state = 'RUNNING-L'
        elif self.acc[0] <= 0 and abs(self.vel[0]) > 1 and self.vel[0] > 0:
            self.state = 'DEC-R'
        elif self.acc[0] >= 0 and abs(self.vel[0]) > 1 and self.vel[0] < 0:
            self.state = 'DEC-L'
        elif abs(self.acc[0]) > 0 and self.vel[0] == 0:
            if self.acc[0] > 0:
                self.state = 'PUSH-R'
            elif self.acc[0] < 0:
                self.state = 'PUSH-L'
        elif self.acc[0] == 0 and abs(self.vel[0]) <= 1:
            if self.lastmoved == -1:
                self.state = 'ST-L'
            elif self.lastmoved == 1:
                self.state = 'ST-R'
            
        else:
            self.state = 'UNKNOWN'
        if self.state in self.spritepalette:
            if type(self.spritepalette[self.state]) is int:
                self.playerSprite.first_frame = self.spritepalette[self.state]
                self.playerSprite.last_frame = self.spritepalette[self.state]
                if self.playerSprite.frame != self.playerSprite.first_frame:
                    self.playerSprite.frame = self.playerSprite.first_frame
                
            elif type(self.spritepalette[self.state]) is tuple and len(self.spritepalette[self.state]) == 2:
                self.playerSprite.first_frame = self.spritepalette[self.state][0]
                self.playerSprite.last_frame = self.spritepalette[self.state][1]
                if self.playerSprite.frame not in range(self.playerSprite.first_frame, self.playerSprite.last_frame + 1):
                    self.playerSprite.frame = self.playerSprite.first_frame
                
        self.hit_timeout = self.gametime.give() - self.whenhit                          
        if self.hit_timeout >= 3:
            self.vulnerable = True
            self.neverleft = False
        if 3 - self.hit_timeout <= 0:
            self.hit_timeout = 0
        ########################################################################################################################################################################################
        #Draws out Overlays
        ########################################################################################################################################################################################
        
        if self.dbg_mode:
            dbg_text_list = [('POS: ', self.pos), #List for debug text parameters to display. Format: ('label', value)
                             ('LOC: ', self.player.topleft),
                             ('VEL: ', self.vel),
                             ('VEC: ', (str(self.velvect[0]) + ' @ ' + str(self.velvect[1]) + ' deg')),
                             ('ACC: ', self.acc),
                             ('TW: ', self.timewarp),
                             ('CW/: ', self.collidingwith),
                             ('CAM: ', (round(self.camera[0], 2), round(self.camera[1], 2))),
                             ('CSP: ', (round(self.trackspeedX*self.movecameraX*self.timewarp, 2), round(self.trackspeedY*self.movecameraY*self.timewarp), 2)),
                             ('HEA: ', self.health),
                             ('STA: ', self.state),
                             ('JMP: ', self.jumping),
                             ('VUL: ', self.vulnerable),
                             ('INV: ', round(3 - self.hit_timeout, 2)),
                             ('TME: ',str(int(self.gametime.give() * 1000 / 1000)) + '.' + str(int(self.gametime.give() * 1000 % 1000)).zfill(3)),
                             ('LM:  ', self.lastmoved),
                             ('VIS: ', visibleobjects)]
            for num in range(0, len(dbg_text_list)):
                label = self.myFont.render(dbg_text_list[num][0] + str(dbg_text_list[num][1]), 1, self.BLACK)
                self.surf.blit(label, (0, self.charheight * num))

        pygame.draw.rect(self.surf, self.BLACK, self.curtainrect, 0) #"curtain drop" animation
        self.surf.blit(self.titletext, (self.titlerect.x, self.titlerect.y))
        ########################################################################################################################################################################################
        #Event Handler and Window Operations (self.clock, frame draws, etc)
        ########################################################################################################################################################################################

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if self.alive: #Only allows movement if character is self.alive.
                
                    if keys[K_SPACE]:
                        if not self.jumping and not self.crouching:
                            self.jumping = True
                            self.vel = (self.vel[0], self.vel[1] - 25 * self.timewarp)
                            
                    if keys[K_a]:
                        if not self.crouching:
                            self.direction = -1
                        self.lastmoved = -1

                    if keys[K_d]:
                        if not self.crouching:
                            self.direction = 1
                        self.lastmoved = 1

                    if keys[K_s]:
                        if not self.crouching:
                            self.pos = (self.pos[0], self.pos[1] + (self.playerheight - self.crouchingheight))
                        self.crouching = True

                    if keys[K_RIGHT]:
                        self.movecameraX = 1
                        self.manualcam = True
                        self.trackspeedX = 10
                    if keys[K_LEFT]:
                        self.movecameraX = -1
                        self.manualcam = True
                        self.trackspeedX = 10
                    if keys[K_UP]:
                        self.movecameraY = -1
                        self.manualcam = True
                        self.trackspeedY = 10
                    if keys[K_DOWN]:
                        self.movecameraY = 1
                        self.manualcam = True
                        self.trackspeedY = 10

                    if not keys[K_DOWN] and not keys[K_UP] and not keys[K_LEFT] and not keys[K_RIGHT]:
                        self.manualcam = False

                    if keys[K_ESCAPE] and self.cancollide:
                        self.vel = (0, -12)
                        self.cancollide = False

            
            if event.type == pygame.KEYUP:
                if event.key == K_a or event.key == K_d:
                    self.direction = 0
                if event.key == K_LEFT or event.key == K_RIGHT:
                    self.movecameraX = 0
                if event.key == K_UP or event.key == K_DOWN:
                    self.movecameraY = 0
                if event.key == K_s:
                    if self.crouching:
                        self.pos = (self.pos[0], self.pos[1] - (self.playerheight - self.crouchingheight))
                    self.crouching = False

                
            
                    
        self.clock.tick(60)
        self.ticks = pygame.time.get_ticks()
        pygame.display.update()
        self.gametime.adv()
        
SCREEN = pygame.display.set_mode((800, 700))
pygame.display.set_caption('Flippy The Penguin')
myGame = Level(SCREEN)
paused = False
while True:
    buttons = pygame.mouse.get_pressed()
    
    if buttons != (0, 0, 0):
        paused = True
    else:
        paused = False
        
    if paused:

        pygame.display.update()
        if pygame.event.peek(QUIT):
                pygame.quit()
                sys.exit()
                
    if not paused:
        myGame.run()
    




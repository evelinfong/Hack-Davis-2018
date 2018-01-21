import pygame, sys
import random
import time 

# Import SPI library (for hardware SPI) and the MCP3008 library 
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
from pygame.locals import *

pygame.init()
pygame.font.init()

myfont = pygame.font.SysFont('Comic Sans MS', 70)

# Hardware SPI configuration:
SPI_PORT = 1
SPI_DEVICE = 0

mcp = Adafruit_MCP3008.MCP3008(spi = SPI.SpiDev(SPI_PORT, SPI_DEVICE))

FPS = 30 # frames per second setting
fpsClock = pygame.time.Clock()
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
TOLERANCE = 30

# set up the window
DISPLAYSURF = pygame.display.set_mode((320, 240), FULLSCREEN)
pygame.display.set_caption('Animation')

WHITE = (255, 255, 255)

class GameManager():
    def __init__(self):
        self.state = 0
        self.level = 1
        self.draw_to_screen_list = []
        self.write_to_screen_list = []
        self.simonPos = []
        self.userPos = []
        self.joystick = InputDevice()
        self.oldTime = time.time()
        self.iteration = 0
        self.isNeutral = False
        self.textsurface = myfont.render("", False, (0, 0, 0))

    def input(self):
        self.joystick.getInput()
    
    def update(self):
        self.draw_to_screen_list = []
        if self.state == 0: #display Level Number  
            self.write_to_screen_list.append(["Level " + str(self.level), 80, 100])
            if time.time() - self.oldTime > 2:
                self.write_to_screen_list = []
                self.state = 1
        elif self.state == 1:
            if (time.time() - self.oldTime) > 1 and (time.time() - self.oldTime) < 2:
                self.draw_to_screen_list.append(cow)
            
            if time.time() - self.oldTime > 2:
                if self.iteration == self.level + 2:
                    self.state = 2
                    self.isNeutral = False
                    print("enter input: " + str(self.simonPos))
                else:
                    self.simonPos.append(cow.random_position())
                    self.oldTime= time.time()
                    self.iteration += 1
        else:
            if self.isNeutral == False: 
                if (512 - TOLERANCE) < self.joystick.xvalue and self.joystick.xvalue < (512 + TOLERANCE) and (512 - TOLERANCE) < self.joystick.yvalue and self.joystick.yvalue <(512 + TOLERANCE):
                    self.isNeutral = True
            else:

                if TOLERANCE > self.joystick.xvalue:
                    self.userPos.append("right")
                    self.isNeutral = False
                elif (1024 - TOLERANCE) < self.joystick.xvalue:
                    self.userPos.append("left")
                    self.isNeutral = False
                elif  TOLERANCE > self.joystick.yvalue:
                    self.userPos.append("up")
                    self.isNeutral = False
                elif (1024 - TOLERANCE) < self.joystick.yvalue:
                    self.userPos.append("down")
                    self.isNeutral = False
                
                if self.isNeutral == False:
                    self.draw_to_screen_list.append(cowtip)
                    self.compareMove()
                else:
                    cow.x = int(float(abs(1024 - self.joystick.xvalue)) / 1024.0 * float(SCREEN_WIDTH)) - cow.width / 2
                    cow.y = int(float(self.joystick.yvalue) / 1024.0 * float(SCREEN_HEIGHT)) - cow.height / 2
                    self.draw_to_screen_list.append(cow)
                
                if len(self.simonPos) == len(self.userPos):
                    self.level += 1
                    self.state = 0
                    self.userPos = []
                    self.simonPos = []
                    self.iteration = 0
                    self.oldTime = time.time()
                    print("start level " + str(self.level))

    def compareMove(self):
        print(self.userPos)
        if self.simonPos[len(self.userPos) -1] != self.userPos[len(self.userPos) - 1]:
            print("GAME OVER!")
            sys.exit()

        

    def draw(self):
        DISPLAYSURF.fill(WHITE)
   
        for sprite in self.draw_to_screen_list:
            DISPLAYSURF.blit(sprite.img, (sprite.x, sprite.y))
    
        for string_data in self.write_to_screen_list:
            self.textsurface = myfont.render(string_data[0], False, (0, 0, 0))
            DISPLAYSURF.blit(self.textsurface, (string_data[1], string_data[2]))
            
            
class Sprite():    
    def __init__(self, imgfile):
        self.img = pygame.image.load(imgfile)
        self.width = int(float(self.img.get_width()) * 0.25);
        self.height = int(float(self.img.get_height()) * 0.25);
        self.img = pygame.transform.scale(self.img, (self.width, self.height))
        self.x = 10
        self.y = 10
        self.direction = 'none'
    
    def random_position(self):
        random.seed(a=time.time())
        randNum = random.uniform(0,10)

        if randNum <= 2.5:
            self.y = SCREEN_HEIGHT/2 - self.height/2
            self.x = 0
            return "left"
        elif randNum <= 5.0:
            self.y = SCREEN_HEIGHT/2 - self.height/2
            self.x = SCREEN_WIDTH - self.width
            return "right"
        elif randNum <= 7.5:
            self.y = 0
            self.x = SCREEN_WIDTH/2 - self.width/2
            return "up"
        else:
            self.y = SCREEN_HEIGHT - self.height
            self.x = SCREEN_WIDTH/2 - self.width/2
            return "down"

    def move(self, joystick):
        if joystick.yvalue > 512: #down
            self.direction = 'down'
    
        if joystick.yvalue < 512: #up
            self.direction = 'up'
   
        if self.direction == 'right':
            self.x += 5
        elif self.direction == 'down':
            self.y += 5
        elif self.direction == 'left':
            self.x -= 5
        elif self.direction == 'up':
            self.y -= 5
   


class InputDevice():
    def __init__(self):
        self.xvalue = 512
        self.yvalue = 512

    def getInput(self):
        self.xvalue = mcp.read_adc(2)
        self.yvalue = mcp.read_adc(1)




gm = GameManager()
cow = Sprite("cow1.png")
cowtip = Sprite("cowtip.png")

while True: # the main game loop
   
    gm.input()
    gm.update()
    gm.draw()


    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    fpsClock.tick(FPS)

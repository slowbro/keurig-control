import errno
import fnmatch
import io
import os
import pygame
import stat
import threading
import time
from pygame.locals import *
from subprocess import call  

# fb/ts setup
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV'      , '/dev/fb1')
os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')

# classes
class Icon:

    def __init__(self, name):
      self.name = name
      try:
        self.bitmap = pygame.image.load(iconPath + '/' + name + '.png')
      except:
        pass

class Button:

    def __init__(self, rect, **kwargs):
      self.rect     = rect # Bounds
      self.color    = None # Background fill color, if any
      self.iconBg   = None # Background Icon (atop color fill)
      self.iconFg   = None # Foreground Icon (atop background)
      self.bg       = None # Background Icon name
      self.fg       = None # Foreground Icon name
      self.callback = None # Callback function
      self.value    = None # Value passed to callback
      for key, value in kwargs.iteritems():
        if   key == 'color': self.color    = value
        elif key == 'bg'   : self.bg       = value
        elif key == 'fg'   : self.fg       = value
        elif key == 'cb'   : self.callback = value
        elif key == 'value': self.value    = value

    def selected(self, pos):
      x1 = self.rect[0]
      y1 = self.rect[1]
      x2 = x1 + self.rect[2] - 1
      y2 = y1 + self.rect[3] - 1
      if ((pos[0] >= x1) and (pos[0] <= x2) and
          (pos[1] >= y1) and (pos[1] <= y2)):
        if self.callback:
          if self.value is None: self.callback()
          else:                  self.callback(self.value)
        return True
      return False

    def draw(self, screen):
      if self.color:
        screen.fill(self.color, self.rect)
      if self.iconBg:
        screen.blit(self.iconBg.bitmap, (self.rect[0], self.rect[1]))
      if self.iconFg:
        screen.blit(self.iconFg.bitmap,
          (self.rect[0]+(self.rect[2]-self.iconFg.bitmap.get_width())/2,
           self.rect[1]+(self.rect[3]-self.iconFg.bitmap.get_height())/2))

    def setBg(self, name):
      if name is None:
        self.iconBg = None
      else:
        for i in icons:
          if name == i.name:
            self.iconBg = i
            break


# globals
iconPath = 'icons'
temp = 192
user = None
icons = []


# init
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
screen.fill((255,255,255))

print pygame.display.Info()

temp_font = pygame.font.SysFont('Monospace', 16)
welcome_font = pygame.font.SysFont('Monospace', 12)
buttons = [
    # screen mode 0 - login page
    [],

    # screen mode 1 - main menu
    [
     Button((295,  0,315, 30), bg='check'               ),
     Button((  0, 80, 18,160), bg='slide-left-disabled' ),
     Button((302, 80,320,160), bg='slide-right'         ),
     Button(( 10,200, 24,214), bg='btn-minus'           ),
     Button(( 80,200, 94,214), bg='btn-plus'            ),
     Button(( 24, 80, 89,160), bg='size-7oz'            ),
     Button(( 93, 80,158,160), bg='size-7oz-selected'   ),
     Button((162, 80,227,160), bg='size-7oz'            ),
     Button((231, 80,296,160), bg='size-7oz'            ),
     Button((190,190,310,230), bg='logout'              ),
    ],

    # screen mode 2 - working
    [],

    # screen mode 3 - standby mode
    [],
]

for file in os.listdir(iconPath):
  if fnmatch.fnmatch(file, '*.png'):
    icons.append(Icon(file.split('.')[0]))

# Assign Icons to Buttons, now that they're loaded
for s in buttons:        # For each screenful of buttons...
  for b in s:            #  For each button on screen...
    for i in icons:      #   For each icon...
      if b.bg == i.name: #    Compare names; match?
        b.iconBg = i     #     Assign Icon to Button
        b.bg     = None  #     Name no longer used; allow garbage collection
      if b.fg == i.name:
        b.iconFg = i
        b.fg     = None

screenMode=1
while(True):
    for event in pygame.event.get():
        if(event.type is MOUSEBUTTONDOWN):
            pos = str(pygame.mouse.get_pos())
            screen.fill((255,255,255))
            text = temp_font.render(pos, 1, (10,10,10))
            screen.blit(text, (2,2))
            break
    for i,b in enumerate(buttons[screenMode]):
       b.draw(screen)
    welcome = welcome_font.render('Welcome, Katelyn!', 0, (0,0,0))
    screen.blit(welcome, (5,5))
    temp_txt = temp_font.render(str(temp)+'F', 0, (0,0,0))
    screen.blit(temp_txt, (32,198))
    pygame.display.flip()
#    pygame.image.save(screen, "main.jpg")
#    exit()

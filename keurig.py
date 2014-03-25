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

# init
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
screen.fill((255,255,255))

# fonts
temp_font = pygame.font.SysFont('Monospace', 16)
welcome_font = pygame.font.SysFont('Monospace', 12)
size_font = pygame.font.SysFont('Monospace', 36)

# classes
class Icon:

    def __init__(self, name):
      self.name = name
      try:
        self.bitmap = pygame.image.load(iconPath + '/' + name + '.png')
      except:
        pass

# Text Class
# __init__:
#  size    (W,H)
#  textpos (X,Y), X=-1 for centered
#  font    pygame.[Sys]Font
#  text    string
# getRenderedSurface:
#  antialias int(0,1)
#  color     (R,G,B)
#  returns: pygame.Surface

class Text:
    def __init__(self, size, textpos, font, text, color=(0,0,0)):
        self.size    = size
        self.textposx= textpos[0]
        self.textposy= textpos[1]
        self.font    = font
        self.text    = text
        self.color   = color
        self.surface = pygame.Surface(size, pygame.SRCALPHA, 32)
        self.textsz  = self.font.size(text)
        if (self.textposx == -1):
            self.textposx = (size[0]-self.textsz[0])/2
        rtext = self.font.render(self.text, 1, self.color)
        self.surface.blit(rtext, (self.textposx, self.textposy))

    def getRenderedSurface(self):
        return self.surface

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
      x2 = self.rect[2]
      y2 = self.rect[3]
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
      elif isinstance(self.fg, Text):
        screen.blit(self.fg.getRenderedSurface(), (self.rect[0], self.rect[1]))

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

# callbacks

def changeTemp(updn):
    global temp
    if(updn == 0):
        temp -= 1
    elif(updn == 1):
        temp += 1

print pygame.display.Info()

buttons = [
    # screen mode 0 - login page
    [],

    # screen mode 1 - main menu
    [
     Button((295,  0,315, 30), bg='check'               ),
     Button((  0, 80, 18,160), bg='slide-left-disabled' ),
     Button((302, 80,320,160), bg='slide-right'         ),
     Button(( 10,200, 24,214), bg='btn-minus', cb=changeTemp, value=0 ),
     Button(( 80,200, 94,214), bg='btn-plus',  cb=changeTemp, value=1 ),
     Button(( 24, 80, 89,160), bg='size-frame',          fg=Text((65,80), (-1,6), size_font, "3") ),
     Button(( 93, 80,158,160), bg='size-frame-selected', fg=Text((65,80), (-1,6), size_font, "7") ),
     Button((162, 80,227,160), bg='size-frame',          fg=Text((65,80), (-1,6), size_font, "12") ),
     Button((231, 80,296,160), bg='size-frame',          fg=Text((65,80), (-1,6), size_font, "16") ),
     Button((190,190,310,230), bg='logout', cb=exit     ),
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
#        b.bg     = None  #     Name no longer used; allow garbage collection
      if b.fg == i.name:
        b.iconFg = i
        b.fg     = None

screenMode=1
while(True):
    for event in pygame.event.get():
        if(event.type is MOUSEBUTTONDOWN):
            pos = pygame.mouse.get_pos()
            for b in buttons[screenMode]:
                if b.selected(pos): print("selected button: "+b.bg)

    screen.fill((255,255,255))
    for i,b in enumerate(buttons[screenMode]):
       b.draw(screen)
    welcome = welcome_font.render('Welcome, Katelyn!', 0, (0,0,0))
    screen.blit(welcome, (5,5))
    temp_txt = temp_font.render(str(temp)+'F', 0, (0,0,0))
    screen.blit(temp_txt, (32,198))
    pygame.display.flip()
#    pygame.image.save(screen, "main.jpg")
#    exit()

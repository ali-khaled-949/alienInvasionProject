import pygame as pg
from pygame.sprite import Sprite, Group
from math import sqrt
from random import randint

RED = (255, 0, 0) 
PINK = (255, 128, 128)
ORANGE = (255, 200, 0)
YELLOW = (255, 255, 0)

GREEN = (0, 255, 0)
GREEN_LIGHT = (128, 255, 128)
GREEN_DARK = (40, 255, 40)
GREEN_YELLOW = (128, 255, 0)
GREEN_CYAN = (128, 255, 64)

CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (255, 0, 255)

# colors = [RED, PINK, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE]
# colors = [GREEN, GREEN_LIGHT, GREEN_DARK]


class BarrierPiece(Sprite):
  def __init__(self, game, color, x, y, width, height): 
    super().__init__()
    self.game = game
    self.screen = game.screen
    self.color = color
    self.rect = pg.Rect(x, y, width, height)
    
  def update(self): self.draw()

  def draw(self): 
    pg.draw.rect(self.screen, self.color, self.rect, 0, 0)



class Barrier:
  colors = [GREEN, GREEN_LIGHT, GREEN_DARK, GREEN_CYAN, GREEN_YELLOW, YELLOW]

  @staticmethod
  def randcolor():
    color_index = randint(0, len(Barrier.colors) - 1)
    #  print(f'return color: {color_index} == {Barrier.colors[color_index]}') 
    return Barrier.colors[color_index]

  @staticmethod 
  def top_corners(i, j, factor): return i == 0 and (j == 0 or j == factor - 1)
  # def top_corners(i, j, factor): return False

  @staticmethod
  def mid_arch(i, j, factor): 
    return abs(i - (factor - 1)) <= 2 and (abs(j - factor // 2) <= 1)
  # def mid_arch(i, j, factor): return False

  def __init__(self, game, rect):
    self.alien_lasers = game.alien.lasers
    self.ship_lasers = game.ship.lasers
    #self.alien_lasers = game.alien_lasers
    #self.ship_lasers = game.ship_lasers
    # self.alien_lasers = game.ship.lasers
    self.screen = game.screen    
    self.pieces = Group()
    npieces = 169
    factor = int(sqrt(npieces))
    w, h = rect.w / factor, rect.h / factor
    x, y = rect.left, rect.top
    li = [BarrierPiece(game, Barrier.randcolor(), x + j * w, y + i * h, w, h) for j in range(factor) for i in range(factor)
          if not Barrier.top_corners(i, j, factor) and not Barrier.mid_arch(i, j, factor)]

    for piece in li:
      self.pieces.add(piece)

  def __str__(self): 
    return f'piece at {self.rect} with color {self.color}'

    # self.image = pg.image.load('images/alien0.bmp')
    # self.rect = self.image.get_rect()
    # self.rect.y = self.rect.height
    # self.x = float(self.rect.x)
      
  def hit(self): pass

  def update(self): 
    #collisions = pg.sprite.groupcollide(self.ship_lasers.lasers, self.pieces, True, True)  
    collisions = pg.sprite.groupcollide(self.alien_lasers.laser_group, self.pieces, True, True) 
    collisions = pg.sprite.groupcollide(self.ship_lasers.laser_group, self.pieces, True, True) 
    self.draw()

  def draw(self): 
    for piece in self.pieces:
        piece.draw()
        # pg.draw.rect(self.screen, Barrier.color, piece, 0, 0)
    # pg.draw.rect(self.screen, Barrier.color, self.rect, 0, 0)
    # pg.draw.circle(self.screen, self.settings.bg_color, (self.rect.centerx, self.rect.bottom), self.rect.width/6)


class Barriers:
  def __init__(self, game):
    self.game = game
    self.settings = game.settings
    self.create_barriers()

  def create_barriers(self):     
    width = self.settings.screen_width / 10
    height = 2.0 * width / 4.0
    top = self.settings.screen_height - 2.1 * height

    # rects = []         // NOT Pythonic -- interviewers want to see Pythonic code
    # for i in range(4):
    #   rects[i] = pg.Rect(i * 2 * width + 1.5 * width, top, width, height)

        # Pythonic programming
    self.barriers = [Barrier(game=self.game, rect=pg.Rect(i * 2 * width + 1.5 * width, top, width, height)) for i in range(4)]   # SP w  3w  5w  7w  SP

    # self.barriers = [Barrier(game=self.game, rect=rects[i]) for i in range(4)]

  def hit(self): pass 

  # def set_ship(self, ship):
  #   for barrier in self.barriers: barrier.set_ship(ship)

  # def set_alien_fleet(self, alien_fleet):
  #   for barrier in self.barriers: barrier.set_alien_fleet(alien_fleet)
  
  def reset(self):
    self.create_barriers()

  def update(self):
    for barrier in self.barriers: barrier.update()

  # def draw(self):
#     for barrier in self.barriers: barrier.draw()


import sys, time
import pygame as pg
from settings import Settings 
from ship import Ship
from alien import Aliens
from vector import Vector
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard
from barrier import Barriers
from ufo import UFO
import random



class Game:
  key_velocity = {pg.K_RIGHT: Vector(1, 0), pg.K_LEFT: Vector(-1,  0),
                  pg.K_UP: Vector(0, -1), pg.K_DOWN: Vector(0, 1)}

  def __init__(self):
    pg.init()
    self.settings = Settings()
    self.screen = pg.display.set_mode(
      (self.settings.screen_width, self.settings.screen_height))
    pg.display.set_caption("Alien Invasion")

    self.alien = None
    self.stats = GameStats(game=self)
    self.sb = Scoreboard(game=self)

    self.ship = Ship(game=self)
    self.alien = Aliens(game=self)  
    self.ship.set_aliens(self.alien)
    self.ship.set_sb(self.sb)
    self.game_active = False              # MUST be before Button is created
    self.first = True
    self.play_button = Button(game=self, text='Play')
    self.barriers = Barriers(game=self)
    #self.ufo_group = pg.sprite.Group()
    #self.ufo_exists = False
    #self.ufo_timer = 0
    #self.ufo = None
    
      

  # def create_ufo(self):
  #   if not self.ufo:  # Only create a UFO if there isn't one already
  #     self.ufo = UFO(self)
  #     self.ufo_group.add(self.ufo)
  #   self.ufo = UFO(self)
    
  #   if not self.ufo_exists:
  #     self.ufo = UFO(self)
  #     self.ufo.rect.x = self.settings.screen_width  # Start UFO from the right side of the screen
  #     self.ufo.rect.y = 5  # Start UFO at the top of the screen
  #     self.ufo_group.add(self.ufo)
  #     self.ufo_exists = True  # Set the flag to indicate a UFO exists
  #     self.ufo_timer = pg.time.get_ticks()
        
  def check_events(self):
    for event in pg.event.get(): 
      type = event.type
      if type == pg.KEYUP: 
        key = event.key 
        if key == pg.K_SPACE: self.ship.cease_fire()
        elif key in Game.key_velocity: self.ship.all_stop()
      elif type == pg.QUIT: 
        pg.quit()
        sys.exit()
      elif type == pg.KEYDOWN:
        key = event.key
        if key == pg.K_SPACE: 
          self.ship.fire_everything()
        elif key == pg.K_p: 
          self.play_button.select(True)
          self.play_button.press()
        elif key in Game.key_velocity: 
          self.ship.add_speed(Game.key_velocity[key])
      elif type == pg.MOUSEBUTTONDOWN:
        b = self.play_button
        x, y = pg.mouse.get_pos()
        if b.rect.collidepoint(x, y):
          b.press()
      elif type == pg.MOUSEMOTION:
        b = self.play_button
        x, y = pg.mouse.get_pos()
        b.select(b.rect.collidepoint(x, y))
    
  def restart(self):
    self.screen.fill(self.settings.bg_color)
    self.ship.reset()
    self.alien.reset()
    #self.ufo.reset()
    self.barriers.reset()
    self.settings.initialize_dynamic_settings()
    #self.ufo = None
    

  def game_over(self):
    print('Game Over !')
    pg.mouse.set_visible(True)
    self.play_button.change_text('Play again?')
    self.play_button.show()
    self.first = True
    self.game_active = False
    self.stats.reset()
    self.restart()

  def activate(self): 
    self.game_active = True
    self.first = False
    self.start_time = pg.time.get_ticks()  # Capture the start time when the game is activated

  def play(self):
    finished = False
    self.screen.fill(self.settings.bg_color)
    start_time = pg.time.get_ticks()  # Capture the start time
            
    while not finished:
      self.check_events()    # exits if Cmd-Q on macOS or Ctrl-Q on other OS
      
      if self.game_active or self.first:
          self.first = False
          self.screen.fill(self.settings.bg_color)
          self.ship.update()
          self.sb.update()
          self.barriers.update()
          #self.ufo_group.update()
          #self.ufo_group.draw(self.screen)
          #self.create_ufo()
          #if self.ufo:
          #  self.ufo.update()
          
          
          
          #self.create_ufo()
          self.play_button.update()

      
      pg.display.flip()
      time.sleep(0.02)


if __name__ == '__main__':
  g = Game()
  g.play()


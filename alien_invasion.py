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
from ufo import UFOs
from sound import Sound
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
    self.ufo = None
    self.stats = GameStats(game=self)
    self.sound = Sound()
    self.sb = Scoreboard(game=self)
    self.sb.load_high_score()

    self.ship = Ship(game=self)
    self.alien = Aliens(game=self)  
    self.ufo = UFOs(game=self)  
    self.ship.set_aliens(self.alien)
    #self.ufo.set_ufos(self.ufo)
    self.ship.set_sb(self.sb)
    self.game_active = False              # MUST be before Button is created
    self.first = True
    self.play_button = Button(game=self, text='Play')
    self.barriers = Barriers(game=self)
    #self.ufo_group = pg.sprite.Group()
    #self.ufo_exists = False
    #self.ufo_timer = 0
    #self.ufo = None
    
    self.ufo.create_fleet()  # Ensure the UFO is created
    
      

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
          self.sound.play_laser()
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

  def alien_hit(self):
    for alien in self.aliens.alien_group.sprites():
                if alien.hit:
                    self.sound.play_phaser()
    
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
    self.sound.play_game_over()
    self.show_launch_screen()
    

  def activate(self): 
    self.game_active = True
    self.first = False
    self.start_time = pg.time.get_ticks()  # Capture the start time when the game is activated
    self.sound.play_music("sounds/i_just_need.wav")
  
  def show_launch_screen(self):
      self.screen.fill((0, 0, 0))  # Fill the background with black

      # Load and draw the Space Invaders graphic
      space_invaders_image = pg.image.load('images/spaceimage.png')
      
      space_invaders_rect = space_invaders_image.get_rect()
      space_invaders_rect.center = self.screen.get_rect().center
      self.screen.blit(space_invaders_image, space_invaders_rect)

      self.play_button.draw()  # Draw the Play button
      pg.display.flip()  # Update the display to show the launch screen

      # Wait for the Play button to be clicked
      waiting_for_input = True
      while waiting_for_input and not self.game_active:
          for event in pg.event.get():
              if event.type == pg.QUIT:
                  pg.quit()
                  sys.exit()
              elif event.type == pg.MOUSEBUTTONDOWN:
                  mouse_x, mouse_y = pg.mouse.get_pos()
                  if self.play_button.rect.collidepoint(mouse_x, mouse_y):
                      self.activate()  # This should start the game
                      waiting_for_input = False
  
  def play(self):
    finished = False
    self.show_launch_screen()
    while not finished:
        self.check_events()  # Check for keyboard and mouse events

        if self.game_active or self.first:  # Only update/draw if the game is active or it's the first run
            self.screen.fill(self.settings.bg_color)  # Fill the background
            self.ship.update()  # Update the player's ship
            self.sb.update()  # Update the scoreboard
            self.barriers.update()  # Update any barriers
            self.ufo.update()  # Update the UFO
            self.ufo.lasers.update()  # Update the UFO's lasers, if any
            self.alien.update()  # Update the aliens
        elif not self.game_active and not self.first:  # Show launch screen if game is not active and not the first run
            self.show_launch_screen()

            # Draw the UFO
            self.ufo.update()  # Update the UFOs
            self.ufo.lasers.update()  # Update the UFOs' lasers, if any

            self.play_button.update()  # Update the play button

        pg.display.flip()  # Update the full display Surface to the screen
        time.sleep(0.02)  # Small delay to limit the loop speed


        pg.display.flip()  # Update the full display Surface to the screen
        time.sleep(0.02)  # Small delay to limit the loop speed



if __name__ == '__main__':
  g = Game()
  g.play()


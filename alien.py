import pygame as pg
import sys
from pygame.sprite import Sprite
from vector import Vector 
from random import randint
from lasers import Lasers
from timer import Timer


class Alien(Sprite):
  names = ['bunny', 'pig', 'stalk_eyes', 'w_heart', 'w_pigtails', 'wild_tentacles']
  points = [60, 80, 100, 200, 300, 500]
  images = [pg.image.load(f'images/alien_{name}.png') for name in names] 
  
  
  # TODO add more lines and make changes as needed
  explode500_images = [pg.transform.scale(pg.image.load(f'images/explode_500_0{x}.png'), (80,80)) for x in range(0, 5)]
  explode300_images = [pg.transform.scale(pg.image.load(f'images/explode_300_0{x}.png'), (80,80)) for x in range(0, 5)]
  explode200_images = [pg.transform.scale(pg.image.load(f'images/explode_200_0{x}.png'), (80,80)) for x in range(0, 5)]
  explode100_images = [pg.transform.scale(pg.image.load(f'images/explode_100_0{x}.png'), (80,80)) for x in range(0, 5)]
  explode80_images = [pg.transform.scale(pg.image.load(f'images/explode_80_0{x}.png'), (80,80)) for x in range(0, 5)]
  explode60_images = [pg.transform.scale(pg.image.load(f'images/explode_60_0{x}.png'), (80,80)) for x in range(0, 5)]
  explosionimages = [explode60_images, explode80_images, explode100_images, explode200_images, explode300_images, explode500_images]


  li = [x * x for x in range(1, 11)]

  def __init__(self, game, row, alien_no):
    super().__init__()
    self.game = game 
    self.screen = game.screen
    self.screen_rect = self.screen.get_rect()
    self.settings = game.settings

    self.regtimer = Timer(Alien.images, start_index=randint(0, len(Alien.images) - 1), delta=20)
    no_aliens = len(Alien.images) - 1
    index = alien_no % no_aliens
    self.points = Alien.points[index]
    
    # TODO -- change the next line
    explosion_images_for_points = {
        60: Alien.explode60_images,
        80: Alien.explode80_images,
        100: Alien.explode100_images,
        200: Alien.explode200_images,
        300: Alien.explode300_images,
        500: Alien.explode500_images,
    }
    self.explosiontimer = Timer(explosion_images_for_points[self.points], delta=6, looponce=True)

    #self.explosiontimer = Timer(Alien.explode60_images[index], delta=6, looponce=True)
    self.timer = self.regtimer

    self.image = Alien.images[index]
    self.alien_no = alien_no
    self.rect = self.image.get_rect()

    self.rect.x = self.rect.width
    self.rect.y = self.rect.height 

    self.x = float(self.rect.x)
    self.isdying = False
    self.reallydead = False 

  def laser_offscreen(self, rect): return rect.bottom > self.screen_rect.bottom  

  def laser_start_rect(self):
    rect = self.rect
    rect.midbottom = self.rect.midbottom
    return rect.copy()
  
  def hit(self): 
    self.isdying = True
    self.timer = self.explosiontimer

  def fire(self, lasers):
    # print(f'Alien {self.alien_no} firing laser')
    timer = Timer(Aliens.laser_images, delta=10)
    lasers.add(owner=self, timer=timer)

  def check_edges(self):
    r = self.rect 
    sr = self.screen_rect
    return r.right >= sr.right or r.left < 0
  
  def check_bottom(self): return self.rect.bottom >= self.screen_rect.bottom 
  
  def update(self, v, delta_y):
    self.x += v.x
    self.rect.x = self.x
    self.rect.y += delta_y
    if self.explosiontimer.finished(): self.kill()
    self.draw()

  def draw(self): 
    self.image = self.timer.current_image()
    self.screen.blit(self.image, self.rect)


class Aliens():
  # laser_image_files = [f'images/alien_laser_0{x}.png' for x in range(2)]
  laser_image_files = [f'images/alien_laser_0{x}.png' for x in range(2, 6)]
  laser_images = [pg.transform.scale(pg.image.load(x), (50, 50)) for x in laser_image_files]

  def __init__(self, game):
    self.game = game
    self.screen = game.screen
    self.settings = game.settings 
    self.stats = game.stats
    self.sb = game.sb
    self.aliens_created = 0
    self.v = Vector(self.settings.alien_speed, 0)
    self.laser_timer = Timer(image_list=Aliens.laser_images, delta=10)
    self.lasers = Lasers(game=game, v=Vector(0, 1) * self.settings.laser_speed, 
                         timer=self.laser_timer, owner=self)

    self.alien_group = pg.sprite.Group()
    self.ship = game.ship
    self.alien_firing_now = 0
    self.fire_every_counter = 0
    self.create_fleet()

  def create_alien(self, x, y, row, alien_no):
      alien = Alien(self.game, row, alien_no)
      alien.x = x
      alien.rect.x, alien.rect.y = x, y
      self.alien_group.add(alien)
      
  def empty(self): self.alien_group.empty()

  def reset(self):
    self.alien_group.empty()
    self.lasers.empty()
    self.create_fleet() 
  
  def create_fleet(self):
    self.fire_every_counter = 0
    alien = Alien(self.game, row=0, alien_no=-1)
    alien_width, alien_height = alien.rect.size 

    x, y, row = alien_width, alien_height, 0
    self.aliens_created = 0
    while y < (self.settings.screen_height - 4 * alien_height):
      while x < (self.settings.screen_width - 2 * alien_width):
        self.create_alien(x=x, y=y, row=row, alien_no=self.aliens_created)
        x += self.settings.alien_spacing * alien_width
        self.aliens_created += 1
      x = alien_width
      y += self.settings.alien_spacing * alien_height
      row += 1

  def check_edges(self):
    for alien in self.alien_group.sprites():
      if alien.check_edges(): return True
    return False

  def check_bottom(self):
    for alien in self.alien_group.sprites():
      if alien.check_bottom(): return True
    return False
  
  def update(self):
    delta_y = 0
    if self.check_edges():
      delta_y = self.settings.fleet_drop
      self.v.x *= -1
      
    if self.check_bottom(): self.ship.hit()
    
    # ship lasers taking out aliens
    collisions = pg.sprite.groupcollide(self.alien_group, self.ship.lasers.lasergroup(), False, True)
    if len(collisions) > 0: 
      for alien in collisions:
        self.game.sound.play_phaser()
        alien.hit()
        # index = alien.timer.current_index()
        # points = Alien.points[index]
        points = alien.points
        self.stats.score += points
        # self.stats.score += self.settings.alien_points
      self.sb.prep_score()
      self.sb.check_high_score()

    # laser-laser collisions
    collisions = pg.sprite.groupcollide(self.ship.lasers.lasergroup(), self.lasers.lasergroup(), 
                                        True, True)

    for alien in self.alien_group.sprites():
      alien.update(self.v, delta_y)

    # must have aliens to fire at the ship
    if self.alien_group and self.fire_every_counter % self.settings.aliens_fireevery == 0:
      n = randint(0, len(self.alien_group) - 1)
      self.alien_group.sprites()[n].fire(lasers=self.lasers)
    self.fire_every_counter += 1

    # update the positions of all of the aliens' lasers (the ship updates its own lasers)
    self.lasers.update()

    # no more aliens -- time to re-create the fleet
    if not self.alien_group:
      self.game.sound.play_transition()
      self.lasers.empty()
      self.create_fleet()
      self.settings.increase_speed()
      self.stats.level += 1
      self.sb.prep_level()

    # aliens hitting the ship
    if pg.sprite.spritecollideany(self.ship, self.alien_group):
      self.ship.hit()

    # alien lasers taking out the ship
    if pg.sprite.spritecollideany(self.ship, self.lasers.lasergroup()):
      self.ship.hit()


if __name__ == '__main__':
  print("\nERROR: aliens.py is the wrong file! Run play from alien_invasions.py\n")

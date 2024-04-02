import pygame as pg
import sys
from pygame.sprite import Sprite
from vector import Vector 
from random import randint
from lasers import Lasers
from timer import Timer


class UFO(Sprite):
  names = ['UFO']
  points = [1000]
  #images = [pg.image.load(f'images/alien_{name}.png') for name in names] 
  images = [pg.image.load(f'images/ufo_image.png') for name in names] 

  
  
  # TODO add more lines and make changes as needed
  explode1000_images = [pg.transform.scale(pg.image.load(f'images/explode_1000_0{x}.png'), (80,80)) for x in range(0, 5)]
  
  explosionimages = [explode1000_images]


  li = [x * x for x in range(1, 1)]

  def __init__(self, game, row, ufo_no):
    super().__init__()
    self.game = game 
    self.screen = game.screen
    self.screen_rect = self.screen.get_rect()
    self.settings = game.settings

    self.regtimer = Timer(UFO.images, start_index=randint(0, len(UFO.images) - 1), delta=20)
    no_aliens = len(UFO.images) - 1
    index = ufo_no % no_aliens
    self.points = UFO.points[index]
    
    # TODO -- change the next line
    explosion_images_for_points = {
        1000: UFO.explode1000_images,
    }
    #self.explosiontimer = Timer(explosion_images_for_points[self.points], delta=6, looponce=True)

    #self.explosiontimer = Timer(Alien.explode60_images[index], delta=6, looponce=True)
    self.timer = self.regtimer

    self.image = UFO.images[index]
    self.alien_no = ufo_no
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
    timer = Timer(UFO.laser_images, delta=10)
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


class UFOs():
  # laser_image_files = [f'images/alien_laser_0{x}.png' for x in range(2)]
  laser_image_files = [f'images/alien_laser_0{x}.png' for x in range(2, 6)]
  laser_images = [pg.transform.scale(pg.image.load(x), (50, 50)) for x in laser_image_files]

  def __init__(self, game):
    self.game = game
    self.screen = game.screen
    self.settings = game.settings 
    self.stats = game.stats
    self.sb = game.sb
    self.ufo_created = 0
    self.v = Vector(self.settings.ufo_speed, 0)
    self.laser_timer = Timer(image_list=UFOs.laser_images, delta=10)
    self.lasers = Lasers(game=game, v=Vector(0, 1) * self.settings.laser_speed, 
                         timer=self.laser_timer, owner=self)

    self.ufo_group = pg.sprite.Group()
    self.ufo = game.ufo
    self.ufo_firing_now = 0
    self.fire_every_counter = 0
    self.create_fleet()

  def create_ufo(self, x, y, row, alien_no):
      ufo = UFO(self.game, row, alien_no)
      ufo.x = x
      ufo.rect.x, ufo.rect.y = x, y
      self.alien_group.add(ufo)
      
  def empty(self): self.ufo_group.empty()

  def reset(self):
    self.ufo_group.empty()
    self.lasers.empty()
    self.create_fleet() 
  
  def create_fleet(self):
    self.fire_every_counter = 0
    ufo = UFO(self.game, row=0, alien_no=-1)
    ufo_width, ufo_height = ufo.rect.size 

    x, y, row = ufo_width, ufo_height, 0
    self.ufos_created = 0
    while y < (self.settings.screen_height - 4 * ufo_height):
      while x < (self.settings.screen_width - 2 * ufo_width):
        self.create_ufo(x=x, y=y, row=row, ufo_no=self.ufos_created)
        x += self.settings.ufo_spacing * ufo_width
        self.ufos_created += 1
      x = ufo_width
      y += self.settings.ufo_spacing * ufo_height
      row += 1

  def check_edges(self):
    for ufo in self.ufo_group.sprites():
      if ufo.check_edges(): return True
    return False

  def check_bottom(self):
    for ufo in self.ufo_group.sprites():
      if ufo.check_bottom(): return True
    return False
  
  def update(self):
    delta_y = 0
    if self.check_edges():
      delta_y = self.settings.fleet_drop
      self.v.x *= -1
      
    if self.check_bottom(): self.ufo.hit()
    
    # ship lasers taking out aliens
    collisions = pg.sprite.groupcollide(self.ufo_group, self.ship.lasers.lasergroup(), False, True)
    if len(collisions) > 0: 
      for ufo in collisions:
        ufo.hit()
        # index = ufo.timer.current_index()
        # points = UFO.points[index]
        points = ufo.points
        self.stats.score += points
        # self.stats.score += self.settings.alien_points
      self.sb.prep_score()
      self.sb.check_high_score()

    # laser-laser collisions
    collisions = pg.sprite.groupcollide(self.ship.lasers.lasergroup(), self.lasers.lasergroup(), 
                                        True, True)

    for ufo in self.ufo_group.sprites():
      ufo.update(self.v, delta_y)

    # must have aliens to fire at the ship
    if self.ufo_group and self.fire_every_counter % self.settings.ufos_fireevery == 0:
      n = randint(0, len(self.ufo_group) - 1)
      self.ufo_group.sprites()[n].fire(lasers=self.lasers)
    self.fire_every_counter += 1

    # update the positions of all of the aliens' lasers (the ship updates its own lasers)
    self.lasers.update()

    # no more aliens -- time to re-create the fleet
    if not self.ufo_group:
      self.lasers.empty()
      self.create_fleet()
      self.settings.increase_speed()
      self.stats.level += 1
      self.sb.prep_level()

    # aliens hitting the ship
    if pg.sprite.spritecollideany(self.ufo, self.ufo_group):
      self.ufo.hit()

    # alien lasers taking out the ship
    if pg.sprite.spritecollideany(self.ufo, self.lasers.lasergroup()):
      self.ufo.hit()


if __name__ == '__main__':
  print("\nERROR: aliens.py is the wrong file! Run play from alien_invasions.py\n")

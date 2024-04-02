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
  #images = [pg.image.load(f'images/ufo_{name}.png') for name in names] 
  images = [pg.image.load(f'images/ufo_image.png') for name in names] 
  laser_image_files = [f'images/alien_laser_0{idx}.png' for idx in range(2, 6)]
  #laser_images = [pg.image.load(img_file).convert_alpha() for img_file in laser_image_files]
  laser_images = [pg.transform.scale(pg.image.load(x), (50, 50)) for x in laser_image_files]
  
  
  
  # TODO add more lines and make changes as needed
  explode1000_images = [pg.transform.scale(pg.image.load(f'images/explode_1000_0{x}.png'), (110,110)) for x in range(0, 5)]
  
  explosionimages = [explode1000_images]


  li = [x * x for x in range(1, 1)]

  def __init__(self, game, row, ufo_no):
    super().__init__()
    self.respawn_time = None 
    self.game = game 
    self.screen = game.screen
    self.screen_rect = self.screen.get_rect()
    self.settings = game.settings

    self.regtimer = Timer(UFO.images, start_index=randint(0, len(UFO.images) - 1), delta=20)
    no_ufos = len(UFO.images) - 1
    index = ufo_no * no_ufos
    self.points = UFO.points[index]
    
    # TODO -- change the next line
    explosion_images_for_points = {
        1000: UFO.explode1000_images,
    }
    #self.explosiontimer = Timer(explosion_images_for_points[self.points], delta=6, looponce=True)

    #self.explosiontimer = Timer(ufo.explode60_images[index], delta=6, looponce=True)
    #self.explosiontimer = Timer(explosion_images_for_points[1000], delta=6, looponce=True)
    self.explosiontimer = Timer(explosion_images_for_points[1000], delta=6, looponce=True)

    self.timer = self.regtimer

    self.image = UFO.images[index]
    self.ufo_no = ufo_no
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
     if not self.isdying:
        self.isdying = True
        self.timer = self.explosiontimer  # Switch to the explosion animation
        self.respawn_time = pg.time.get_ticks() + 3000  # Schedule respawn

  def fire(self, lasers):
    # print(f'ufo {self.ufo_no} firing laser')
    timer = Timer(UFO.laser_images, delta=10)
    lasers.add(owner=self, timer=timer)

  def check_edges(self):
    r = self.rect 
    sr = self.screen_rect
    return r.right >= sr.right or r.left < 0
  
  def check_bottom(self): return self.rect.bottom >= self.screen_rect.bottom 
  
  def update(self, v, delta_y):
      # Check if UFO is dying and the explosion animation is finished
        if self.isdying:
            if self.explosiontimer.finished():
                self.kill()  # Removes the UFO from all groups
                self.isdying = False  # Resets the dying state
            else:
                self.explosiontimer.update_index()  # Continue explosion animation
        else:
            self.x += v.x
            self.rect.x = self.x
            self.rect.y += delta_y


  def draw(self):
    if self.isdying and not self.explosiontimer.finished():
        self.image = self.explosiontimer.current_image()
    else:
        self.image = self.timer.current_image()
    self.screen.blit(self.image, self.rect)
    
    #if self.isdying:
    #    self.image = self.explosion_images_for_points  # You need to define this attribute
    #else:
    #    self.image = self.timer.current_image()
    #self.screen.blit(self.image, self.rect)   
    #self.image = self.timer.current_image()
    #self.screen.blit(self.image, self.rect)


class UFOs():
  # laser_image_files = [f'images/ufo_laser_0{x}.png' for x in range(2)]
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

  def create_ufo(self, x, y, row, ufo_no):
      ufo = UFO(self.game, row, ufo_no)
      ufo.x = x
      ufo.rect.x, ufo.rect.y = x, y
      self.ufo_group.add(ufo)
      
  def empty(self): self.ufo_group.empty()

  def reset(self):
    self.ufo_group.empty()
    self.lasers.empty()
    self.create_fleet() 
  
  def create_fleet(self):
     if not self.ufo_group:
        x = self.settings.screen_width / 2
        y = self.settings.screen_height * 0.1
        self.create_ufo(x=x, y=y, row=0, ufo_no=0)
    # Remove the loop and create only one UFO
    #x = self.settings.screen_width / 2
    #y = self.settings.screen_height * 0.1  # Place the UFO at the top 10% of the screen
    #self.create_ufo(x=x, y=y, row=0, ufo_no=0)  # Create a single UFO

  def check_edges(self):
    for ufo in self.ufo_group.sprites():
      if ufo.check_edges(): return True
    return False

  def check_bottom(self):
    for ufo in self.ufo_group.sprites():
      if ufo.check_bottom(): return True
    return False
  
  def update(self):
    current_time = pg.time.get_ticks()
    delta_y = 0
    if self.check_edges():
        self.v.x *= -1
        delta_y = self.settings.fleet_drop

    for ufo in self.ufo_group.sprites():
        # Check for collisions with ship's lasers
        collisions = pg.sprite.groupcollide(self.ufo_group, self.game.ship.lasers.lasergroup(), False, True)
        for hit_ufo in collisions:
            self.game.sound.play_phaser()
            hit_ufo.hit()  # Trigger explosion effect for the hit UFO
            if ufo.explosiontimer.finished():
                ufo.kill()  # Remove the UFO if the explosion animation has finished
                self.ufo_created -= 1
                

        if ufo.isdying:
            if current_time >= ufo.respawn_time:
                ufo.isdying = False
                ufo.rect.x = self.settings.screen_width / 2  # Reset position for respawn
                ufo.rect.y = self.settings.screen_height * 0.1
                ufo.respawn_time = pg.time.get_ticks() + 3000  # Schedule respawn in 3 seconds
                ufo.explosiontimer = Timer(image_list=UFOs.laser_images, delta=10)
                self.ufo_created += 1
                
            continue  # Skip drawing and updating UFOs that are 'dying'

        ufo.x += self.v.x
        ufo.rect.x = ufo.x
        ufo.rect.y += delta_y
        ufo.draw()

    # UFO firing logic
    if self.ufo_group and self.fire_every_counter % self.settings.ufos_fireevery == 0:
        n = randint(0, len(self.ufo_group.sprites()) - 1)
        self.ufo_group.sprites()[n].fire(lasers=self.lasers)
    self.fire_every_counter += 1

    self.lasers.update()  # Update UFO lasers

    # If no UFOs, recreate the fleet (respawn)
    if not self.ufo_group:
        self.create_fleet()

        # Check for collisions with ship's lasers
        collisions = pg.sprite.groupcollide(self.ufo_group, self.game.ship.lasers.lasergroup(), False, True)
        for ufo in collisions:
            ufo.hit() # Trigger explosion effect for the hit UFO

        if ufo.explosiontimer.finished():
            ufo.kill()  # Remove the UFO if the explosion animation has finished
        else:
            ufo.draw()  # Draw the UFO (or its explosion animation)

        # Must have UFOs to fire at the ship
        if self.ufo_group and self.fire_every_counter % self.settings.ufos_fireevery == 0:
            n = randint(0, len(self.ufo_group.sprites()) - 1)
            self.ufo_group.sprites()[n].fire(lasers=self.lasers)
        self.fire_every_counter += 1

        # Update the positions of all of the UFOs' lasers
        self.lasers.update()

        # No more UFOs -- time to re-create the fleet
        if len(self.ufo_group) == 0:
            self.lasers.empty()
            self.create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()


if __name__ == '__main__':
  print("\nERROR: ufos.py is the wrong file! Run play from ufo_invasions.py\n")

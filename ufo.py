import pygame
import sys
from pygame.sprite import Sprite, groupcollide
from vector import Vector
from random import randint
from lasers import Lasers
from timer import Timer
from sound import Sound

class UFO(Sprite):
    names = ['UFO']
    points = [1000]
    images = [pygame.image.load(f'images/ufo_image.png') for name in names] 
    laser_image_files = [f'images/alien_laser_0{idx}.png' for idx in range(2, 6)]
    laser_images = [pygame.transform.scale(pygame.image.load(x), (50, 50)) for x in laser_image_files]
    explode1000_images = [pygame.transform.scale(pygame.image.load(f'images/explode_1000_0{x}.png'), (110,110)) for x in range(0, 5)]
    explosionimages = [explode1000_images]

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
        
        explosion_images_for_points = {
            1000: UFO.explode1000_images,
        }
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
    
    def hit(self, sound):
        if not self.isdying:
            self.isdying = True
            self.timer = self.explosiontimer  # Switch to the explosion animation
            self.respawn_time = pygame.time.get_ticks() + 3000  # Schedule respawn
            self.game.sound.play_punch()  # Trigger the punch sound effect
            
    def fire(self, lasers):
        timer = Timer(UFO.laser_images, delta=10)
        lasers.add(owner=self, timer=timer)

    def check_edges(self):
        r = self.rect 
        sr = self.screen_rect
        return r.right >= sr.right or r.left < 0
    
    def check_bottom(self): return self.rect.bottom >= self.screen_rect.bottom 
    
    def update(self, v, delta_y):
        current_time = pygame.time.get_ticks()
        if self.isdying:
            if current_time >= self.respawn_time:
                self.isdying = False
                self.rect.x = self.settings.screen_width / 2  # Reset position for respawn
                self.rect.y = self.settings.screen_height * 0.1
                self.respawn_time = pygame.time.get_ticks() + 3000  # Schedule respawn in 3 seconds
                self.explosiontimer = Timer(image_list=UFO.laser_images, delta=10)
            return  # Skip drawing and updating UFOs that are 'dying'

        self.x += v.x
        self.rect.x = self.x
        self.rect.y += delta_y

    def draw(self):
        if self.isdying:
            self.image = self.explosiontimer.current_image()
        else:
            self.image = self.timer.current_image()
        self.screen.blit(self.image, self.rect)

class UFOs:
    laser_image_files = [f'images/alien_laser_0{x}.png' for x in range(2, 6)]
    laser_images = [pygame.transform.scale(pygame.image.load(x), (50, 50)) for x in laser_image_files]

    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.settings = game.settings 
        self.stats = game.stats
        self.sb = game.sb
        self.ufo_created = 0
        self.v = Vector(self.settings.ufo_speed, 0)
        self.laser_timer = Timer(image_list=UFO.laser_images, delta=10)
        self.lasers = Lasers(game=game, v=Vector(0, 1) * self.settings.laser_speed, 
                             timer=self.laser_timer, owner=self)

        self.ufo_group = pygame.sprite.Group()
        self.ufo_firing_now = 0
        self.fire_every_counter = 0
        self.create_fleet()
        self.screen_rect = self.screen.get_rect()
        self.sound = game.sound

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

    def check_edges(self):
      for ufo in self.ufo_group.sprites():
        if ufo.rect.right >= self.screen_rect.right or ufo.rect.left < 0:
            return True
      return False

    def update(self):
        current_time = pygame.time.get_ticks()
        delta_y = 0
        if self.check_edges():
            self.v.x *= -1
            self.game.sound.play_ufo()
            delta_y = self.settings.fleet_drop

        for ufo in self.ufo_group.sprites():
            ufo.update(self.v, delta_y)
            ufo.draw()

        if self.ufo_group and self.fire_every_counter % self.settings.ufos_fireevery == 0:
            n = randint(0, len(self.ufo_group.sprites()) - 1)
            self.ufo_group.sprites()[n].fire(lasers=self.lasers)
        self.fire_every_counter += 1

        self.lasers.update()

        if not self.ufo_group:
            self.create_fleet()

        collisions = groupcollide(self.ufo_group, self.game.ship.lasers.lasergroup(), False, True)
        for ufo in collisions:
            #ufo.hit() # Trigger explosion effect for the hit UFO
            ufo.hit(self.sound) 

        for ufo in self.ufo_group:
            if ufo.isdying and ufo.explosiontimer.finished():
                ufo.kill()  # Remove the UFO if the explosion animation has finished

        if len(self.ufo_group) == 0:
            self.create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()
        
        for ufo in collisions:
          ufo.hit(self.sound)


if __name__ == '__main__':
    print("\nERROR: ufos.py is the wrong file! Run play from ufo_invasions.py\n")

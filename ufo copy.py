import pygame as pg
import random
from timer import Timer
from vector import Vector
from lasers import Lasers


class UFO(pg.sprite.Sprite):
    laser_image_files = [f'images/alien_laser_0{x}.png' for x in range(2, 6)]
    laser_images = [pg.transform.scale(pg.image.load(x), (50, 50)) for x in laser_image_files]
    
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.screen = game.screen
        self.settings = game.settings 
        self.stats = game.stats
        self.sb = game.sb
        self.aliens_created = 0
        self.v = Vector(self.settings.alien_speed, 0)
        self.laser_timer = Timer(image_list=UFO.laser_images, delta=10)
        self.lasers = Lasers(game=game, v=Vector(0, 1) * self.settings.laser_speed, 
                            timer=self.laser_timer, owner=self)
        self.image = pg.image.load('images/ufo_image.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, self.game.settings.screen_width - self.rect.width)
        self.rect.y = 20
        self.speed = random.choice([-5, 5])
        self.points = 1000
        self.exploding = False
        self.alien_group = pg.sprite.Group()
        self.ufo = game.ufo
        self.ufo_firing_now = 0
        self.fire_every_counter = 0

        # Load explosion images
        self.explode_images = [pg.transform.scale(pg.image.load(f'images/explode_1000_0{x}.png'), (80, 80)) for x in range(5)]
        self.explosiontimer = Timer(self.explode_images, delta=100, looponce=True)

    def update(self):
        if not self.exploding:
            self.rect.x += self.speed
            if self.rect.left <= 0 or self.rect.right >= self.game.settings.screen_width:
                self.speed *= -1
            hits = pg.sprite.spritecollide(self, self.game.ship.lasers.lasergroup(), True)
            if hits:
                self.exploding = True
                self.game.stats.score += self.points
                self.game.sb.prep_score()
                self.game.sb.check_high_score()

        else:
            # Only check the timer if the UFO is exploding
            if self.explosiontimer.finished():
                self.kill()
            else:
                self.image = self.explosiontimer.imagerect().image
                
    collisions = pg.sprite.groupcollide(self.ufo_group, self.ufo.lasers.lasergroup(), False, True)
    if len(collisions) > 0: 
      for ufo in collisions:
        ufo.hit()
        # index = alien.timer.current_index()
        # points = Alien.points[index]
        points = ufo.points
        ufo.stats.score += points
        # self.stats.score += self.settings.alien_points
        ufo.sb.prep_score()
        ufo.sb.check_high_score()

        # laser-laser collisions
    collisions = pg.sprite.groupcollide(self.ufo.lasers.lasergroup(), self.lasers.lasergroup(), 
                                        True, True)


    def hit(self): 
        self.exploding = True
        self.image = self.explode_images[0]  # Start with the first explosion image


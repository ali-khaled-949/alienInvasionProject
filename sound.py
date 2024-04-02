import pygame as pg
from pygame import mixer 
import time


class Sound:
    def __init__(self):
        mixer.init() 
        self.ufo_sound = mixer.Sound("sounds/st_ufo.wav")
        self.punch_sound = mixer.Sound("sounds/st_punch.wav")
        self.phaser_sound = mixer.Sound("sounds/st_phaser.wav")
        self.laser_sound = mixer.Sound("sounds/sw_laser.wav")
        self.trans_sound = mixer.Sound("sounds/transition.wav")
        self.volume = 0.1
        self.set_volume(self.volume)        
    
    def set_volume(self, volume=0.3):
        mixer.music.set_volume(volume) 
        self.punch_sound.set_volume(3 * volume)
        self.phaser_sound.set_volume(3 * volume)
        self.ufo_sound.set_volume(3 * volume)
        self.laser_sound.set_volume(3 * volume)
        self.trans_sound.set_volume(3 * volume)

    def play_music(self, filename): 
        self.stop_music()
        mixer.music.load(filename) 
        mixer.music.play(loops=-1) 
 
    def pause_music(self): 
        mixer.music.pause()

    def unpause_music(self):
        mixer.music.unpause()      

    def stop_music(self): 
        mixer.music.stop() 
 
    def play_phaser(self): 
        mixer.Sound.play(self.phaser_sound)
    
    def play_punch(self): 
        mixer.Sound.play(self.punch_sound)
            
    def play_ufo(self): 
        mixer.Sound.play(self.ufo_sound)

    def play_laser(self):
        mixer.Sound.play(self.laser_sound)


    def play_transition(self):
        mixer.Sound.play(self.trans_sound) 

    def play_game_over(self):
        self.stop_music()
        self.play_music("sounds/game_over.wav")
        time.sleep(6.5)
        self.stop_music()
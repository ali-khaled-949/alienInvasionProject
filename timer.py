class Timer: 
  def __init__(self, image_list, start_index=0, delta=6, looponce=False): 
    self.image_list = image_list
    self.delta = delta
    self.looponce = looponce
    self.index = start_index
    self.time = 0

  def update_index(self):
     self.time += 1
     if self.time >= self.delta:
      self.time = 0
      if not self.finished():  # Check if the animation is not finished
        self.index += 1
        if self.index >= len(self.image_list):  # Reset or stop the index at the end of the list
          if self.looponce:
             self.index = len(self.image_list) - 1  # Keep the index at the last frame for looponce
          else:
             self.index = 0  # Loop back to the start of the list

  def finished(self): 
    return self.looponce and self.index == len(self.image_list) - 1
  def current_index(self): return self.index

  def current_image(self):     # self.time = 0
    self.update_index()
    return self.image_list[self.index]
  

# TImerDual does NOT inherit from Timer -- instead, it HAS two Timer instances inside of it 
class TimerDual:
  def __init__(self, image_list0, image_list1, start_index0=0, start_index1=0, delta0=6, delta1=6, delta_timers=100, looponce0=False, looponce1=False):
    self.timer0 = Timer(self, image_list=image_list0, start_index=start_index0, delta=delta0, looponce=looponce0)
    self.timer1 = Timer(self, image_list=image_list1, start_index=start_index1, delta=delta1, looponce=looponce1)
    # TODO
    #self.timer0 = Timer(image_list0, start_index=start_index0, delta=delta0, looponce=looponce0)
    self.timer1 = Timer(image_list1, start_index=start_index1, delta=delta1, looponce=looponce1)


  def update_index(self): pass   # TODO -- remove pass and put in your code (if needed)
  
  def finished(self): pass       # TODO -- remove pass and put in your code (if needed)
  
  def current_timer(self): pass  # TODO -- remove pass and put in your code (if needed)
  
  def current_index(self): pass  # TODO -- remove pass and put in your code (if needed)
  
  def current_image(self): pass  # TODO -- remove pass and put in your code (if needed)
  
import pygame

class DuckGuy():
  def __init__(self):
    self.hp = 4
    self.state = "idle"
  def punch(self):
    self.state = "punching"
  def unpunch(self):
    self.state = "idle"


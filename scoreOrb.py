import random
import math
import time
scoreOrbList = []
#Take the score orb and turn it into a usable object
class ScoreOrb:
  def __init__(self, orbType, radius, x, y):
    self.score = 0
    self.color = ()
    self.radius = radius
    self.x = x
    self.y = y
    self.orbType = orbType
    self.orgsTouched = []

    if self.orbType == "POSITIVE":
      self.score = 1000
      self.color = (0, 255, 0)
    elif self.orbType == "NEGATIVE":
      self.score = -1000
      self.color = (255, 0, 0)
    elif self.orbType == "RANDOM":
      self.score = math.floor(random.gauss(0, 100))
      # print (self.score)
      self.color = (255, 255, 0)

#Detect when a org is touching the scoreOrb
  def intersects(self, other):
    x = other.x
    y = other.y
    r = other.radius
    sx = self.x
    sy = self.y
    sr = self.radius

    if other in self.orgsTouched:
      return

    if math.sqrt((sx - x)**2 + (sy - y)**2)<=r+sr:
      other.score += self.score
      other.update()
      self.orgsTouched.append(other)

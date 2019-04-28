import random
import math
scoreOrbList = []
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
      self.orgsTouched.append(other)

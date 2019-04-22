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

    if self.orbType == "Positive":
      self.score = 10
      self.color = (0, 255, 0)
    elif self.orbType == "Negative":
      self.score = -10
      self.color = (255, 0, 0)
    elif self.orbType == "Random":
      self.score = math.floor(random.gauss(0, 50))
      # print (self.score)
      self.color = (255, 255, 0)

  def intersects(self, other):
    x = other.x
    y = other.y
    r = other.radius
    sx = self.x
    sy = self.y
    sr = self.radius
    
    if math.sqrt((sx - x)**2 + (sy - y)**2)<=r+sr:
      other.score += self.score
      scoreOrbList.remove(self)

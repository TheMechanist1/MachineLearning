import math
import gameGraphics
import raytracing

class Organism:
  """An organism"""
  def __init__(self, org):
    self.name = org['name']
    self.generation = org['generation']
    self.naturalGeneration = org['naturalGeneration']
    self.namespace = org['namespace']
    self.ownerUsername = org['owner_username']
    self.score = org['score']
    self.speciesNamespace = org['speciesNamespace']
    self.trainingRoomNamespace = org['trainingRoomNamespace']
    self.ttl = org['ttl']
    self.nNet = org['nNet']
    self.neuralNetwork = NeuralNet(self.nNet)
    self.x = 350
    self.y = 250
    self.radius = 10
    self.color = (255, 0, 0)
    self.rotation = 0

  def turnOutput(self, degrees):
    self.rotation = degrees

  def moveOutput(self, weight):
    x_movement = weight*math.cos(self.rotation * (math.pi / 180))
    self.x += x_movement
    for reg in gameGraphics.wall_regions:
      while self.intersects(reg):
        if x_movement > 0:
          self.x -= 1
        else:
          self.x += 1

    y_movement = weight*math.sin(self.rotation * (math.pi / 180))
    self.y -= y_movement
    for reg in gameGraphics.wall_regions:
      while self.intersects(reg):
        if y_movement > 0:
          self.y += 1
        else:
          self.y -= 1

  def intersects(self, region):
    x, y, w, h = region
    sx = self.x - self.radius
    sy = self.y - self.radius
    sw = self.radius * 2
    return sx < x + w and sx + sw > x and sy < y + h and sy + sw > y

class NeuralNet:
  """The neural net of a Organism"""
  def __init__(self, nNet):
    neurons = {}
    self.outputs = []
    self.inputs = []
    self.weight = 0

    for currentNeuron in nNet['neurons']:
      neuro = Neuron(currentNeuron)
      if neuro._base_type == "output":
        self.weight = neuro.average
        self.outputs.append(neuro)
      elif neuro._base_type == "input":
        self.inputs.append(neuro)
      neurons[neuro.id] = neuro

    self.eyes = []
    for biologyNode in nNet['biology']:
      if biologyNode['$TYPE'] == 'eye':
        self.eyes.append(Eye(biologyNode))


class Neuron:
  """A node of a neural network"""
  def __init__(self, thisNeuron):
      self.type = thisNeuron['$TYPE']
      self._base_type = thisNeuron['_base_type']
      self.id = thisNeuron['id']
      self.full = thisNeuron
      if self._base_type == "output":
        self.deps = thisNeuron['dependencies']
        weights = [i['weight'] for i in self.deps]
        average = sum(weights) / len(weights)
        self.average = average

class Biology:
  """An abstract biology node"""
  def __init__(self, data):
    self.type = data['$TYPE']
    self.id = data['id']

class Eye(Biology):
  colors = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (127, 127, 0),
  ]

  def __init__(self, data):
    super().__init__(data)
    self.distance = float(data['distance'])
    self.direction = float(data['lookDirection'])
    color_index = int(data['color'])
    self.color = Eye.colors[color_index]
    self.index = float(data['index'])

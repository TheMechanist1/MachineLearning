import math
import gameGraphics
import random

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
    self.y = 400
    self.radius = 10
    self.color = (255, 0, 0)
    self.rotation = random.randint(0, 360)

  def turnOutput(self, weight):
    if weight > 0.5:
      self.rotation = (1 / (1 + math.exp(weight))) * 180

  def moveOutput(self, weight):
    x_movement = (math.cos(self.rotation * (math.pi / 180)))*weight
    self.x += x_movement
    for reg in gameGraphics.wall_regions:
      while self.intersects(reg):
        if x_movement > 0:
          self.x -= 1
        else:
          self.x += 1

    y_movement = (math.sin(self.rotation * (math.pi / 180)))*weight
    self.y -= y_movement
    for reg in gameGraphics.wall_regions:
      while self.intersects(reg):
        if y_movement > 0:
          self.y += 1
        else:
          self.y -= 1
  
  def sidwaysMoveOutput(self, weight):
    x_movement = (math.sin(self.rotation * (math.pi / 180)))*weight
    self.x += x_movement
    for reg in gameGraphics.wall_regions:
      while self.intersects(reg):
        if x_movement > 0:
          self.x -= 1
        else:
          self.x += 1

    y_movement = (math.cos(self.rotation * (math.pi / 180)))*weight
    self.y -= y_movement
    for reg in gameGraphics.wall_regions:
      while self.intersects(reg):
        if y_movement > 0:
          self.y += 1
        else:
          self.y -= 1

  def intersects(self, region):
    x = region[0]
    y = region[1]
    w = region[2]
    h = region[3]
    sx = self.x - self.radius
    sy = self.y - self.radius
    sw = self.radius * 2
    return sx < x + w and sx + sw > x and sy < y + h and sy + sw > y

class NeuralNet:
  """The neural net of a Organism"""
  def __init__(self, nNet):
    neurons = {}
    self.outputs = []
    self.outputDict = {}
    self.inputs = []
    self.inputDict = {}
    # self.weight = 0
    self.neuronEvalDepth = -1

    for currentNeuron in nNet['neurons']:
      neuron = Neuron(self, currentNeuron)
      if neuron._base_type == "output":
        # self.weight = neuron.average
        self.outputs.append(neuron)
        self.outputDict[neuron.id] = neuron
      elif neuron._base_type == "input":
        self.inputs.append(neuron)
        self.inputDict[neuron.id] = neuron
      neurons[neuron.id] = neuron

    self.eyes = []
    self.eyesDict = {}
    for biologyNode in nNet['biology']:
      if biologyNode['$TYPE'] == 'eye':
        eye = Eye(biologyNode)
        self.eyes.append(eye)
        self.eyesDict[eye.id] = eye
  
  def evaluate(self):
    for outputs in self.outputs:
      outputs.reset()

    for outputs in self.outputs:
      if outputs._base_type == "output":
        _last_value = outputs.evaluate()
        outputs._lastValue = _last_value


class Neuron:
  """A node of a neural network"""
  def __init__(self, network, thisNeuron):
    self.network = network
    self.hasBeenEvaluated = False
    self._lastValue = -1
    self.type = thisNeuron['$TYPE']
    self._base_type = thisNeuron['_base_type']
    self.id = thisNeuron['id']
    self.full = thisNeuron
    if self._base_type == "output":
      self.deps = []
      for dep in thisNeuron['dependencies']:
        self.deps.append(Dependency(self.network, dep))
      # weights = [i.weight for i in self.deps]
      # average = sum(weights) / len(weights)
      # self.average = average
      self.weight = 0
    if self._base_type == "input":
      self.attributeId = thisNeuron['attributeId']
      self.attributeValue = thisNeuron['attributeValue']
    if 'eye' in thisNeuron:
      self.eyeId = thisNeuron['eye']

  def evaluate(self):
    # if self.hasBeenEvaluated:
    #   return self._lastValue
    if self._base_type == 'input':
      value = self.network.eyesDict[self.eyeId].value
      return value * 2 - 1
    elif self._base_type == 'output':
      totalScore = 0

      for dep in self.deps:
        dep._lastValue = dep.evaluate()
        totalScore += dep._lastValue

      self._lastValue = (1 / (1 + math.exp(totalScore))) 
      self.hasBeenEvaluated = True

      self.weight = self._lastValue * 2 - 1
      return self._lastValue

  def reset(self):
    self.hasBeenEvaluated = False
    self._lastValue = -1

class Dependency:
  def __init__(self, network, data):
    self.neuronId = data['neuronId']
    self.input = network.inputDict[self.neuronId]
    self.weight = float(data['weight'])
    self.originalNaturalGen = data['_originNaturalGen']
    self.originGen = data['_originGen']

  def evaluate(self):
    return self.input.evaluate() * self.weight

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
    self.value = 0

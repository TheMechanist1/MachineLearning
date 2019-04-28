import math
import gameGraphics
import random
import time

class Stats:
  def __init__(self, stat):
    self.speciesCreated = stat['speciesCreated']
    self.totalOrgsPerGen = stat['totalOrgsPerGen']
    self.orgsSpawnedSoFar = stat['orgsSpawnedSoFar']
    self.orgsReportedSoFar = stat['orgsReportedSoFar']
    self.orgsToSpawn = stat['orgsToSpawn']
    self.orgsLeftToReport = stat['orgsLeftToReport']
    self.genProgress = stat['genProgress']

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
    self.x = 350 + random.randint(-300, 300)
    self.y = 350 + random.randint(-300, 300)
    self.radius = 10
    self.color = (0, 0, 0)
    self.rotation = 0 #random.randint(0, 360)
    self.spawnedFrame = gameGraphics.frames
    self.time = 0
    self.maxFrames = 15 * 60

  def to_json(self):
    orgJson = {"namespace":self.namespace, "score": str(self.score)}
    return orgJson


  def turnOutput(self, weight):
    if weight > 0.5 or weight < -0.5:
      self.rotation += weight

  def moveOutput(self, weight):
    x_movement = math.cos(weight*180)
    self.x += x_movement
    for reg in gameGraphics.wall_regions:
      while self.intersects(reg):
        if x_movement > 0:
          self.x -= 1
        else:
          self.x += 1

    y_movement = math.sin(weight*180)
    self.y -= y_movement
    for reg in gameGraphics.wall_regions:
      while self.intersects(reg):
        if y_movement > 0:
          self.y += 1
        else:
          self.y -= 1
  
  def sidwaysMoveOutput(self, weight):
    x_movement = math.sin(weight*180)
    self.x += x_movement
    for reg in gameGraphics.wall_regions:
      while self.intersects(reg):
        if x_movement > 0:
          self.x -= 1
        else:
          self.x += 1

    y_movement = math.cos(weight*180)
    self.y -= y_movement
    for reg in gameGraphics.wall_regions:
      while self.intersects(reg):

          # self.neuralNetwork.orgList.remove(self)
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
    self.middles = []
    self.middleDict = {}
    # self.weight = 0
    self.neuronEvalDepth = -1

    for currentNeuron in nNet['neurons']:
      neuron = Neuron(self, currentNeuron)
      if neuron._base_type == "output":
        # self.weight = neuron.average
        out = Output(self, currentNeuron)
        self.outputs.append(out)
        self.outputDict[out.id] = neuron
      elif neuron._base_type == "input":
        inp = Input(self, currentNeuron)
        self.inputs.append(inp)
        self.inputDict[inp.id] = neuron
      elif neuron._base_type == "middle":
        mid = Middle(self, currentNeuron)
        self.middles.append(mid)
        self.middleDict[mid.id] = neuron
      neurons[neuron.id] = neuron
    
    self.eyes = []
    self.eyesDict = {}
    self.colors = []
    self.colorDict = {}
    for biologyNode in nNet['biology']:
      if biologyNode['$TYPE'] == 'eye':
        eye = Eye(biologyNode)
        self.eyes.append(eye)
        self.eyesDict[eye.id] = eye
      if biologyNode['$TYPE'] == 'color':
        color = Color(biologyNode)
        self.colors.append(color)
        self.colorDict[color.id] = color
  
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

    self.deps = []
    if 'dependencies' in thisNeuron:
      for dep in thisNeuron['dependencies']:
        self.deps.append(Dependency(self.network, dep))
      self.weight = 0

    if 'eye' in thisNeuron:
      self.eyeId = thisNeuron['eye']

    

  def evaluate(self):
    # if self.hasBeenEvaluated:
    #   return self._lastValue
    if self._base_type == 'input':
      value = self.network.eyesDict[self.eyeId].value
      return value * 2 - 1
    elif self._base_type == 'output' or self._base_type == 'middle':
      totalScore = 0

      for dep in self.deps:
        if dep != -1:
          dep._lastValue = dep.evaluate()
          totalScore += dep._lastValue

        self._lastValue = (1 / (1 + math.exp(totalScore))) 
        self.hasBeenEvaluated = True

        self.weight = self._lastValue * 2 - 1
        return self._lastValue

  def reset(self):
    self.hasBeenEvaluated = False
    self._lastValue = -1

class Input(Neuron):
  def __init__(self, network, thisNeuron):
    super().__init__(network, thisNeuron)
    self.attributeId = thisNeuron['attributeId']
    self.attributeValue = thisNeuron['attributeValue']

class Middle(Neuron):
  def __init__(self, network, thisNeuron):
    super().__init__(network, thisNeuron)

    
class Output(Neuron):
  def __init__(self, network, thisNeuron):
    super().__init__(network, thisNeuron)

class Dependency:
  def __init__(self, network, data):
    self.neuronId = data['neuronId']
    
    
    self._last_value = -1
    self.weight = float(data['weight'])
    self.originalNaturalGen = data['_originNaturalGen']
    self.originGen = data['_originGen']
    self.input = -1

    if self.neuronId in network.inputDict:
      self.input = network.inputDict[self.neuronId]
    elif self.neuronId in network.outputDict:
      self.input = network.outputDict[self.neuronId]
    elif self.neuronId in network.middleDict:
      self.input = network.middleDict[self.neuronId]

  def evaluate(self):
    if self.input != -1:
      return self.input.evaluate() * self.weight
    else:
      return -1
    

class Biology:
  """An abstract biology node"""
  def __init__(self, data):
    self.type = data['$TYPE']
    self.id = data['id']

class Eye(Biology):
  def __init__(self, data):
    super().__init__(data)
    self.direction = float(data['lookDirection'])
    self.index = float(data['index'])
    self.value = 0

class Color(Biology):
  def __init__(self, data):
    super().__init__(data)
    self.color = (int(data['r']), int(data['g']), int(data['b']))
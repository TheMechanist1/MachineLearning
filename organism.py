import math
import gameGraphics
import random
import time

#Take the stats and turn it into a usable object
class Stats:
  def __init__(self, stat):
    self.speciesCreated = stat['speciesCreated']
    self.totalOrgsPerGen = stat['totalOrgsPerGen']
    self.orgsSpawnedSoFar = stat['orgsSpawnedSoFar']
    self.orgsReportedSoFar = stat['orgsReportedSoFar']
    self.orgsToSpawn = stat['orgsToSpawn']
    self.orgsLeftToReport = stat['orgsLeftToReport']
    self.genProgress = stat['genProgress']

#Take the organism and turn it into a usable object
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
    self.rotation = random.randint(0, 360)
    self.spawnedFrame = gameGraphics.frames
    self.time = 0
    self.maxFrames = 15 * 60

  def to_json(self):
    orgJson = {"namespace":self.namespace, "score": str(self.score)}
    return orgJson

#Turns at a speed determained by the lastValue
#TODO: rewrite this function because it sucks and the orgs cant learn with it
  def turnOutput(self, weight):
    if weight > 0.5 or weight < -0.5:
      self.rotation += weight

#Takes the lastvalue to move the organism up or down
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
  
  #Takes the lastvalue to move the organism left or right
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
        if y_movement > 0:
          self.y += 1
        else:
          self.y -= 1

#My intersect function to check if the organism is touching a wall or a orb
  def intersects(self, region):
    x = region[0]
    y = region[1]
    w = region[2]
    h = region[3]
    sx = self.x - self.radius
    sy = self.y - self.radius
    sw = self.radius * 2
    return sx < x + w and sx + sw > x and sy < y + h and sy + sw > y

#Class to turn my NeuralNetwork into a usable object
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
    self.neuronEvalDepth = -1
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

    for currentNeuron in nNet['neurons']:
      neuron = Neuron(self, currentNeuron)
      if neuron._base_type == "output":
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

#small function to make sure I am always evaluating
#TODO: Something is wrong with one of these evaluate functions cause the lastValue never changes. Gotta look into this eventualy
  def evaluate(self):
    
    for output in self.outputs:
      output._lastValue = output.outputEvaluate()
      
class Neuron:
  """A node of a neural network"""
  def __init__(self, network, thisNeuron):
    self.network = network
    self._lastValue = 0
    self.weight = 0
    self.type = thisNeuron['$TYPE']
    self._base_type = thisNeuron['_base_type']
    self.id = thisNeuron['id']
    self.full = thisNeuron

    self.deps = []

    if 'eye' in thisNeuron:
      self.eyeId = thisNeuron['eye']

    if 'dependencies' in thisNeuron:
      for dep in thisNeuron['dependencies']:
        self.deps.append(Dependency(self.network, dep))
        
  #Evaluate the last value of the output neuron and also do the weights but that doesnt matter as of now
  def outputEvaluate(self):
    value = 0
    weight = 0
    
    for depend in self.deps:
      if self._lastValue != -100:
        value += depend._last_value
        weight += depend.depweight
    if len(self.deps) != 0:
      self.weight = weight / len(self.deps)
    value = self.sigmoid(value)
    return value

#Sigmoid but with a check to make sure I dont get a outofbounds exeption
  def sigmoid(self, i):
    sig = 0
    if i > 0:
      sig = (1) / (1 + math.exp(-i))
    if i < 0:
      sig = (1 - 1/(1 + math.exp(i)))
    return sig
    

    


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
    self.depweight = float(data['weight'])
    self._last_value = -100
    if self.neuronId in network.inputDict:
      self.input = network.inputDict[self.neuronId]
      if self.input.eyeId in network.eyesDict:
        self.eye = network.eyesDict[self.input.eyeId]
        self._last_value = self.evaluateDep()
    elif self.neuronId in network.middleDict:
      self.input = network.middleDict[self.neuronId]
    

  def evaluateDep(self):
    print(str(self.depweight) + " " + str(self.eye.value))
    return self.depweight * self.eye.value
      
    
    
    

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
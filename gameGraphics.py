#Made by GarboMuffin
# Import a library of functions called 'pygame'
import pygame
import organism
import random
import math
import time
import json
import chaosapi
import scoreOrb

scoredOrgs = []
jsonMes = ''
wall_regions = [
    # x, y, w, h, name, color
    [0, 0, 700, 25, "BLACK_WALL", (0, 0, 0)],
    [0, 0, 25, 700, "BLUE_WALL", (0, 0, 255)],
    [675, 0, 25, 700, "RED_WALL", (255, 0, 0)],
    [0, 675, 700, 25, "GREEN_WALL", (0, 255, 0)],
]

def point_intersects_wall(x, y):
    for region in wall_regions:
        wx = region[0]
        wy = region[1]
        ww = region[2]
        wh = region[3]
        wall_type = region[4]
        if x < wx + ww and x > wx and y < wy + wh and y > wy:
            return True, wall_type
    return False, None

def distance_to_wall(x, y, direction, max_dist):
    cos = math.cos(direction * math.pi / 180)
    sin = math.sin(direction * math.pi / 180)
    for distance in range(0, int(max_dist)):
        new_x = x + cos * distance
        new_y = y + sin * distance
        inter = point_intersects_wall(new_x, new_y)
        if inter[0]:
            return distance, inter[1]
        
    return -1, None

organismList = []
scoreOrbList = []

def mainGraphicsLoop():
    # Initialize the game engine
    pygame.init()
    
    orgsani = chaosapi.setup()
    organ = orgsani[0]
    for org in organ['organisms']:
        organismList.append(organism.Organism(org))
    
    scoreOrbList.append(scoreOrb.ScoreOrb(10, 350, 350))

    #set window peramiters and open the window
    size = (700, 700)
    screen = pygame.display.set_mode(size)

    # Loop until the user clicks the close button.
    done = False
 
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('Comic Sans MS', 15)
 
    # -------- Main Program Loop -----------
    while not done:
        # --- Main event loop
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done = True # Flag that we are done so we exit this loop

        screen.fill((255, 255, 255))

        for region in wall_regions:
            pygame.draw.rect(screen, region[5], (region[0], region[1], region[2], region[3]))
        
        if len(scoreOrbList) != 0:
            for scoreOrbs in scoreOrbList:
                pygame.draw.circle(screen, (0, 255, 0), (scoreOrbs.x, scoreOrbs.y), 5)

        encoded = []
        if len(organismList) <= 0:
            for score in scoredOrgs:
                encoded.append(score.to_json())
            
            scoredOrgs.clear()
            organismList.clear()
            jsonMes = json.dumps({"report": encoded})
            newOrgs = chaosapi.reportOrgs('mechanist', 'finalRoom', orgsani[1], orgsani[2], jsonMes)
            for orgsi in newOrgs['organisms']:
                organismList.append(organism.Organism(orgsi))
            
        for org in organismList[:]:
            color = (255, 0, 0)
            textsurface = font.render(str(org.trainingRoomNamespace), False, (255, 255, 255))
            screen.blit(textsurface, (0,0))

            org.time = time.monotonic()
            if org.time - org.spawnedTime >= org.maxTime:
                scoredOrgs.append(org)
                organismList.remove(org)

            org.neuralNetwork.evaluate()

            # Read & handle outputs
            for output in org.neuralNetwork.outputs:
                if output.type == 'TurnOutput':
                    org.turnOutput(output.weight)
                if output.type == 'MoveOutput':
                    org.moveOutput(output.weight)
                if output.type == 'MoveSidewaysOutput':
                    org.sidwaysMoveOutput(output.weight)
                

            # Show the player's location before drawing eyes
            pygame.draw.circle(screen, org.color, (int(org.x), int(org.y)), org.radius)
            
            view_x = org.x + math.cos(org.rotation * math.pi / 180) * org.radius * 2
            view_y = org.y - math.sin(org.rotation * math.pi / 180) * org.radius * 2
            pygame.draw.line(screen, (0, 0, 0), (org.x, org.y), (view_x, view_y), 2)
            
            # Render eyes
            eye = None
            for i in org.neuralNetwork.inputs:
                eyeID = i.eyeId
                eyeValue = i.attributeValue
            for eyes in org.neuralNetwork.eyes:
                if eyes.id == eyeID:
                    eye = eyes
                    
            eyeDirection = eye.direction + -org.rotation
            distance = 100 + org.radius
            distance_x = math.cos(eyeDirection * math.pi / 180) * distance
            distance_y = math.sin(eyeDirection * math.pi / 180) * distance
            x = org.x + distance_x
            y = org.y + distance_y

            trace_x = org.x + math.cos(eyeDirection * math.pi / 180) * org.radius
            trace_y = org.y + math.sin(eyeDirection * math.pi / 180) * org.radius
            trace_distance = distance - org.radius
            eye_to_wall = distance_to_wall(trace_x, trace_y, eyeDirection, trace_distance)

            if eye_to_wall[0] == -1:
                value = 0
            elif eyeValue == eye_to_wall[1]:
                value = (trace_distance - eye_to_wall[0]) / trace_distance
                color = (0, 255, 0)
            else:
                value = 0
            eye.value = value

            pygame.draw.line(screen, color, (trace_x, trace_y), (x, y), 2)
            textsurface = font.render(str(org.generation) + " " + str(org.score), False, (0, 0, 0))
            screen.blit(textsurface, (x,y))


        #update the screen
        pygame.display.flip()
 
        #60 frames per second
        #TODO: add a function to make this go faster for faster sim times
        #clock.tick(60)

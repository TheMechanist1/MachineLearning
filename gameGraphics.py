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
import profiler

organismList = []
scoreOrbList = []
frames = 0
totalOrgs = 0
screenWidth = 800
screenHeight = 800
scoredOrgs = []

wall_regions = [
    # x, y, w, h, name, color
    [0, 0, screenWidth, 25, "RED_WALL", (255, 0, 0)],
    [0, 0, 25, screenHeight, "RED_WALL", (255, 0, 0)],
    [screenWidth - 25, 0, 25, screenHeight, "RED_WALL", (255, 0, 0)],
    [0, screenHeight - 25, screenWidth, 25, "RED_WALL", (255, 0, 0)],
    [0, screenHeight - 100, screenWidth - 75, 25, "RED_WALL", (255, 0, 0)],
]

def point_intersects_wall(x, y, region):
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
    for distance in range(0, int(max_dist), 16):
        new_x = x + cos * distance
        new_y = y + sin * distance
        for region in wall_regions:
            inter = point_intersects_wall(new_x, new_y, region)
            if inter[0]:
                return distance, inter[1]
        
    return -1, None

def distance_to_orb(x, y, direction, max_dist):
    cos = math.cos(direction * math.pi / 180)
    sin = math.sin(direction * math.pi / 180)
    for distance in range(0, int(max_dist), 16):
        new_x = x + cos * distance
        new_y = y + sin * distance
        for orb in scoreOrb.scoreOrbList:
            inter = point_intersects_wall(new_x + orb.radius, new_y+orb.radius, [orb.x, orb.y, orb.radius*2, orb.radius*2, orb.orbType])
            if inter[0]:
                return distance, inter[1]
        
    return -1, None

scoreOrb.scoreOrbList = [
    scoreOrb.ScoreOrb("POSITIVE", 10, 50, 750),
    scoreOrb.ScoreOrb("POSITIVE", 10, 150, 750),
    scoreOrb.ScoreOrb("POSITIVE", 10, 250, 750),
    scoreOrb.ScoreOrb("POSITIVE", 10, 350, 750),
    scoreOrb.ScoreOrb("POSITIVE", 10, 450, 750),
    scoreOrb.ScoreOrb("POSITIVE", 10, 550, 750),
    scoreOrb.ScoreOrb("POSITIVE", 10, 650, 750),
    scoreOrb.ScoreOrb("POSITIVE", 10, 750, 750),

    scoreOrb.ScoreOrb("POSITIVE", 10, 750, 650),
    scoreOrb.ScoreOrb("POSITIVE", 10, 750, 550),
    scoreOrb.ScoreOrb("POSITIVE", 10, 750, 450),
    scoreOrb.ScoreOrb("POSITIVE", 10, 750, 350),
    scoreOrb.ScoreOrb("POSITIVE", 10, 750, 250),
]

def mainGraphicsLoop():
    global frames, totalOrgs

    # Initialize the game engine
    pygame.init()
    
    orgsani = chaosapi.setup()
    organ = orgsani[0]
    for org in organ['organisms']:
        organismList.append(organism.Organism(org))
    totalOrgs = organ['stats']['orgsSpawnedSoFar']

    #set window peramiters and open the window
    size = (screenWidth, screenWidth)
    screen = pygame.display.set_mode(size)

    # Loop until the user clicks the close button.
    done = False
 
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('Comic Sans MS', 15)
 
    # -------- Main Program Loop -----------
    while not done:

        frames += 1
        
        # --- Main event loop
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done = True # Flag that we are done so we exit this loop
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for org in organismList:
                        scoredOrgs.append(org)
                    organismList.clear()
                   

        profiler.start('everything')

        screen.fill((255, 255, 255))

        for region in wall_regions:
            pygame.draw.rect(screen, region[5], (region[0], region[1], region[2], region[3]))

        for scoreOrbs in scoreOrb.scoreOrbList:
            pygame.draw.circle(screen, scoreOrbs.color, (scoreOrbs.x, scoreOrbs.y), scoreOrbs.radius)
            textsurface = font.render(str(scoreOrbs.score), False, (0, 0, 0))
            screen.blit(textsurface,(scoreOrbs.x,scoreOrbs.y))

        encoded = []
        if len(organismList) <= 0:
            for score in scoredOrgs:
                encoded.append(score.to_json())

            scoredOrgs.clear()
            organismList.clear()
            jsonMes = json.dumps({"report": encoded})
            newOrgs = chaosapi.reportOrgs('mechanist', 'finalRoom', orgsani[1], orgsani[2], jsonMes)
            totalOrgs = newOrgs['stats']['orgsSpawnedSoFar']
            for orgsi in newOrgs['organisms']:
                organismList.append(organism.Organism(orgsi))

        profiler.start('organisms')
        for org in organismList[:]:
            org.neuralNetwork.evaluate()

            color = (255, 0, 0)
            textsurface = font.render(str(org.trainingRoomNamespace), False, (255, 255, 255))
            orgAmount = font.render(str(totalOrgs) + " / 2000", False, (255, 255, 255))
            screen.blit(textsurface, (0,0))
            screen.blit(orgAmount, (70,0))

            if(frames - org.timeSinceLastScore) >= org.maxFrames:
                scoredOrgs.append(org)
                organismList.remove(org)
                continue

            for scoreOrbs in scoreOrb.scoreOrbList:
                scoreOrbs.intersects(org)

            # Read & handle outputs
            for output in org.neuralNetwork.outputs:
                
                if output.type == 'TurnOutput':
                    org.turnOutput(output._lastValue)
                if output.type == 'MoveOutput':
                    org.moveOutput(output._lastValue)
                if output.type == 'MoveSidewaysOutput':
                    org.sidwaysMoveOutput(output._lastValue)

            # Show the player's location before drawing eyes
            pygame.draw.circle(screen, org.color, (int(org.x), int(org.y)), org.radius)

            view_x = org.x + math.cos(org.rotation * math.pi / 180) * org.radius * 2
            view_y = org.y - math.sin(org.rotation * math.pi / 180) * org.radius * 2
            pygame.draw.line(screen, (0, 0, 0), (org.x, org.y), (view_x, view_y), 2)
            
            for color in org.neuralNetwork.colors:
                org.color = color.color
            # Render eyes
            for i in org.neuralNetwork.inputs:
                eyeValue = i.attributeValue
                eye = org.neuralNetwork.eyesDict[i.eyeId]

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
                eye_to_orb = distance_to_orb(trace_x, trace_y, eyeDirection, trace_distance)
                #While looking at nothing turn a weird purplish color
                if eye_to_wall[0] == -1 and eye_to_orb[0] == -1:
                    value = 0
                    color = (123, 57, 199)
                
                #While looking at a wall that is the same as the eyeValue turn green and change the value
                elif eyeValue == eye_to_wall[1]:
                    value = (trace_distance - eye_to_wall[0]) / trace_distance
                    color = (0, 255, 0)

                #While looking at an orb that is the same as the eyeValue turn cyan and change the value
                elif eyeValue == eye_to_orb[1]:
                    value = (trace_distance - eye_to_orb[0]) / trace_distance
                    color = (0, 255, 255)

                #While looking at something else turn yellow
                else:
                    value = 0
                    color = (123, 57, 199)
                eye.value = value

                pygame.draw.line(screen, color, (trace_x, trace_y), (x, y), 2)
                
                score = font.render(str(org.score), False, (0, 0, 0))
                screen.blit(score,(org.x,org.y))
        profiler.end()
        profiler.end()
        #update the screen
        pygame.display.flip()

 
        #60 frames per second
        #TODO: add a function to make this go faster for faster sim times
        # clock.tick(60)

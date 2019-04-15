# Import a library of functions called 'pygame'
import pygame
import organism
import random
import math

wall_regions = [
    [0, 0, 700, 25],
    [0, 0, 25, 500],
    [675, 0, 25, 500],
    [0, 475, 700, 25],
]

def mainGraphicsLoop(organisms):
    # Initialize the game engine
    pygame.init()

    #Colors for pygame
    BLACK = (   0,   0,   0)
    WHITE = ( 255, 255, 255)
    GREEN = (   0, 255,   0)
    RED = ( 255,   0,   0)
    BLUE = (   0,   0, 255)

    #set window peramiters and open the window
    size = (700, 500)
    screen = pygame.display.set_mode(size)

    # Loop until the user clicks the close button.
    done = False
 
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
 
    # -------- Main Program Loop -----------
    while not done:
        # --- Main event loop
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done = True # Flag that we are done so we exit this loop

        screen.fill(WHITE)

        for region in wall_regions:
            pygame.draw.rect(screen, BLACK, region)

        for org in organisms:
            # Read & handle outputs
            for output in org.neuralNetwork.outputs:
                if output.type == 'TurnOutput':
                    org.turnOutput(output.average*180)
                elif output.type == 'MoveOutput':
                    org.moveOutput(output.average)

            # Show the player's location before drawing eyes
            pygame.draw.circle(screen, org.color, (int(org.x), int(org.y)), org.radius)

            # Render eyes
            for eye in org.neuralNetwork.eyes:
                eyeDirection = eye.direction + org.rotation
                distance = eye.distance*10 + org.radius
                distance_x = math.cos(eyeDirection * math.pi / 180) * distance
                distance_y = math.sin(eyeDirection * math.pi / 180) * distance
                x = org.x + distance_x
                y = org.y + distance_y
                pygame.draw.line(screen, eye.color, (org.x, org.y), (x, y), 2)


        #update the screen
        pygame.display.flip()
 
        #60 frames per second
        #TODO: add a function to make this go faster for faster sim times
        clock.tick(60)

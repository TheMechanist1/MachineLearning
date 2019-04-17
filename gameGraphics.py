#Made by GarboMuffin
# Import a library of functions called 'pygame'
import pygame
import organism
import random
import math

wall_regions = [
    # x, y, w, h, name
    [0, 0, 700, 25, ""],
    [0, 0, 25, 500, ""],
    [675, 0, 25, 500, ""],
    [0, 475, 700, 25, ""],
    [46, 50, 600, 25, ""],
]

def point_intersects_wall(x, y):
    for region in wall_regions:
        wx, wy, ww, wh = region
        if x < wx + ww and x > wx and y < wy + wh and y > wy:
            return True
    return False

def distance_to_wall(x, y, direction, max_dist):
    cos = math.cos(direction * math.pi / 180)
    sin = math.sin(direction * math.pi / 180)
    for distance in range(0, int(max_dist)):
        new_x = x + cos * distance
        new_y = y + sin * distance
        if point_intersects_wall(new_x, new_y):
            return distance
    return -1


def mainGraphicsLoop(organisms):
    # Initialize the game engine
    pygame.init()

    #set window peramiters and open the window
    size = (700, 500)
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
            pygame.draw.rect(screen, (0, 0, 0), region)

        for org in organisms:
            org.neuralNetwork.evaluate()

            # Read & handle outputs
            for output in org.neuralNetwork.outputs:
                if output.type == 'TurnOutput':
                    org.turnOutput(output.weight*180)
                elif output.type == 'MoveOutput':
                    org.moveOutput(output.weight)

            # Show the player's location before drawing eyes
            pygame.draw.circle(screen, org.color, (int(org.x), int(org.y)), org.radius)
            
            view_x = org.x + math.cos(org.rotation * math.pi / 180) * org.radius * 2
            view_y = org.y + math.sin(org.rotation * math.pi / 180) * org.radius * 2
            pygame.draw.line(screen, (0, 0, 0), (org.x, org.y), (view_x, view_y), 2)

            # Render eyes
            for eye in org.neuralNetwork.eyes:
                eyeDirection = eye.direction
                distance = eye.distance*20 + org.radius
                distance_x = math.cos(eyeDirection * math.pi / 180) * distance
                distance_y = math.sin(eyeDirection * math.pi / 180) * distance
                x = org.x + distance_x
                y = org.y + distance_y

                trace_x = org.x + math.cos(eyeDirection * math.pi / 180) * org.radius
                trace_y = org.y + math.sin(eyeDirection * math.pi / 180) * org.radius
                trace_distance = distance - org.radius
                eye_to_wall = distance_to_wall(trace_x, trace_y, eyeDirection, trace_distance)

                if eye_to_wall == -1:
                    value = 0
                else:
                    value = (trace_distance - eye_to_wall) / trace_distance
                eye.value = value

                pygame.draw.line(screen, (0, 200, (value)*255), (trace_x, trace_y), (x, y), 2)
                #textsurface = font.render(str(value), False, (0, 0, 255))
                #screen.blit(textsurface, (x,y))


        #update the screen
        pygame.display.flip()
 
        #60 frames per second
        #TODO: add a function to make this go faster for faster sim times
        clock.tick(60)

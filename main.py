import chaosapi
import gameGraphics
import time
import math
import organism
import argparse

organismList = []

parser = argparse.ArgumentParser(description='aa')
parser.add_argument('--password')
parser.add_argument('--username')
args = parser.parse_args()

#Begin setup timer
start = time.time()

#Get our auth token from chaosnet
print("Logging in and getting token...")
authToken = chaosapi.login(args.username, args.password)

#Start the session and get the namespace
print("Starting session and getting namespace...")
nameSpace = chaosapi.startSession('mechanist', 'finalRoom', authToken)

#Get our organisms for later use
print("Getting the organisms...")
getOrganisms = chaosapi.getOrganisms('mechanist', 'finalRoom', authToken, nameSpace)

#End setup timer
end = time.time()

#Get the time it took to setup
print("Setup took about " + str(round((end - start), 3)) + " seconds")

for org in getOrganisms['organisms']:
    organismList.append(organism.Organism(org))


#start the screen
gameGraphics.mainGraphicsLoop(organismList)



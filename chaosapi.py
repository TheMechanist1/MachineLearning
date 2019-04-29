import requests
import os
import json
import argparse
import time

args = ()

#Do a post and get the authToken useing the inputed username and password
#TODO: dont forget to remove your password and username Dylan >:(
def login(username, password):
    if os.path.exists('cachedlogin'):
        with open('cachedlogin') as f:
            content = f.read()
            print('Using cached access token')
            return content
    
    print('Fetching new access token')

    r = requests.post('https://chaosnet.schematical.com/v0/auth/login', json={'username':username, 'password':password})
    response = r.json()
    if r.status_code != 200:
        print("Error! Got a status-code of " + str(r.status_code) + "\nTraceback:" + str(response))
        return

    accessToken = response['accessToken']
    with open('cachedlogin', 'w+') as f:
        f.write(accessToken)
    return accessToken

#Uses the authToken we got from the login def to start a new session which will give us the namespace
def startSession(username, trainingroom, auth, bool):
    if bool:
        requests.post('https://chaosnet.schematical.com/v0/'+username+'/trainingrooms/'+trainingroom+'/sessions/start', headers={'Authorization':auth}, json={'reset': 'true'})
        r = requests.post('https://chaosnet.schematical.com/v0/'+username+'/trainingrooms/'+trainingroom+'/sessions/start', headers={'Authorization':auth})
    else:
        r = requests.post('https://chaosnet.schematical.com/v0/'+username+'/trainingrooms/'+trainingroom+'/sessions/start', headers={'Authorization':auth})
    response = r.json()
    if r.status_code != 200:
        if r.status_code == 401:
            os.remove("cachedlogin")
            authToken = login(args.username, args.password)
        print("Error! Got a status-code of " + str(r.status_code) + "\nTraceback:" + str(response))
        return

    return response['namespace']

#Uses the namespace, trainingroom, and auth to give us the list of organisms' brains that we'll use in the future
def getOrganisms(username, trainingroom, auth, namespace):
    r = requests.post('https://chaosnet.schematical.com/v0/'+username+'/trainingrooms/'+trainingroom+'/sessions/'+namespace+'/next', headers={'Authorization':auth})
    response = r.json()
    if r.status_code != 200:
        print("Error! Got a status-code of " + str(r.status_code) + "\nTraceback:" + str(response))
        return

    return response

#report orgs and get back a new set of orgs. use data to go to next set and use json to stay on this set
def reportOrgs(username, trainingroom, auth, namespace, orgjson):
    r = requests.post('https://chaosnet.schematical.com/v0/'+username+'/trainingrooms/'+trainingroom+'/sessions/'+namespace+'/next', headers={'Authorization':auth}, data=orgjson)
    response = r.json()
    if r.status_code != 200:
        if r.status_code == 401:
            os.remove("cachedlogin")
            authToken = login(args.username, args.password)

        print("Error! Got a status-code of " + str(r.status_code) + "\nTraceback:" + str(response))
        return
    return response

#setup all the stuff and things
def setup():
    parser = argparse.ArgumentParser(description='aa')
    parser.add_argument('--password')
    parser.add_argument('--username')
    args = parser.parse_args()

    #Begin setup timer
    start = time.time()

    #Get our auth token from chaosnet
    print("Logging in and getting token...")
    authToken = login(args.username, args.password)

    #Start the session and get the namespace
    print("Starting session and getting namespace...")
    nameSpace = startSession('mechanist', 'finalRoom', authToken, False)

    #Get our organisms for later use
    print("Getting the organisms...")
    orgs = getOrganisms('mechanist', 'finalRoom', authToken, nameSpace)

    #End setup timer
    end = time.time()

    #Get the time it took to setup
    print("Setup took about " + str(round((end - start), 3)) + " seconds")

    return [orgs, authToken, nameSpace]
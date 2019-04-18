import requests
import os

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
def startSession(username, trainingroom, auth):
    r = requests.post('https://chaosnet.schematical.com/v0/'+username+'/trainingrooms/'+trainingroom+'/sessions/start', headers={'Authorization':auth})
    response = r.json()
    if r.status_code != 200:
        if r.status_code == 401:
            os.remove("cachedlogin")
            return
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

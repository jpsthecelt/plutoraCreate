#!/usr/bin/python

import requests
import pprint
import argparse
import json

#
# This is a sample program intended to demonstrate creating a system in Plutora
# it requires previously 'set up' access to Plutora (client_id and client_secret, etc)
#

def createSystem(cfgFilename, clientid, clientsecret, PlutoraUsername, PlutoraPassword):
    # Set up JSON prettyPrinting
    pp = pprint.PrettyPrinter(indent=4)
    
    # Setup to obtain Get authorization-token
    authTokenUrl = "https://usoauth.plutora.com/oauth/token"
    payload = 'client_id=' + clientid + '&client_secret=' + clientsecret + '&grant_type=password&username='
    payload = payload + PlutoraUsername + '&password=' + PlutoraPassword + '&='
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'postman-token': "bc355474-15d1-1f56-6e35-371b930eac6f"
        }
    
    # Connect to get Plutora access token for subsequent queries
    authResponse = requests.post(authTokenUrl, data=payload, headers=headers)
    if authResponse.status_code != 200:
        print('Get auth-release status code: %i' % authResponse.status_code)
        print('plSuystemCreate.py: Sorry! - [failed on getAuthToken]: ', authResponse.text)
        exit('Sorry, unrecoverable error; gotta go...')
    else:
        print('\nplSuystemCreate.py - authTokenGet: ')
        pp.pprint(authResponse.json())
        accessToken = authResponse.json()["access_token"]
    
    # Setup to query Maersk Plutora instances
    plutoraBaseUrl= 'https://usapi.plutora.com'
    plutoraMaerskUrl = r'http://maersk.plutora.com/changes/12/comments'
    plutoraMaerskTestUrl = r'https://usapi.plutora.com/me'
    #jiraURL = r'http://localhost:8080/rest/api/2/search?jql=project="DemoRevamp"&expand'
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "authorization": "bearer "+accessToken,
        "cache-control": "no-cache",
        "postman-token": "bc355474-15d1-1f56-6e35-371b930eac6f"
    }
    
    # Experiment -- Get Plutora information for all system releases, or systems, or just the organization-tree
    getReleases = '/releases/9d18a2dc-b694-4b20-971f-4944420f4038'
    getSystems = '/systems'
    getOrganizationsTree = '/organizations/tree'
    
    r = requests.get(plutoraBaseUrl+getOrganizationsTree, data=payload, headers=headers)
    if r.status_code != 200:
        print('Get release status code: %i' % r.status_code)
        print('\npltSystemCreate.py: too bad sucka! - [failed on Plutora get]')
        exit('Sorry, unrecoverable error; gotta go...')
    else:
        print('\npltSystemCreate.py - Plutora get of organizations information:')
        pp.pprint(r.json())

    # Experiment -- Get Plutora information for all hosts
    getHosts = '/hosts'
    getOrganizationsTree = '/organizations/tree'

#    r = requests.get(plutoraBaseUrl+getHosts, data=payload, headers=headers)
#    if r.status_code != 200:
#        print('Get release status code: %i' % r.status_code)
#        print('\npltSystemCreate.py: too bad sucka! - [failed on Plutora gethosts]')
#        exit('Sorry, unrecoverable error; gotta go...')
#    else:
#        print('\npltSystemCreate.py - Plutora get of hosts information:')
#        pp.pprint(r.json())

# OK; try creating a new system...
    try:
        headers["content-type"] = "application/json"
        payload = """{ "name": "API created System 12", "vendor": "API created vendor", "status": "Active", "organizationId": "%s", "description": "Description of API created System 12" }""" % r.json()['childs'][0]['id']

        postSystem = '/systems'
        print("Here's what I'm sending Plutora (headers & payload):")
        print("header: ",headers)
        print("payload: ",payload)
        
        r = requests.post(plutoraBaseUrl+postSystem, data=json.loads(payload), headers=headers)
        if r.status_code != 200:
            print('Post new system status code: %i' % r.status_code)
            print('\npltSystemCreate.py: too bad sucka! - [failed on Plutora create system POST]')
            print("header: ",headers)
            pp.pprint(r.json())
            exit('Sorry, unrecoverable error; gotta go...')
        else:
            print('\npltSystemCreate.py - Plutora POST of new system information:')
            pp.pprint(r.json())
    except Exception,ex:
        # ex.msg is a string that looks like a dictionary
        print "EXCEPTION: %s " % ex.msg
        exit('Error during API processing [POST]')
        
# Residual stuff follows:
#for i in r.json()["issues"]:
#    print("field is", i["fields"]["description"])
#    r = requests.post(plutoraMaerskUrl, data=i["fields"]["description"], headers=headers)
#    if r.status_code != 200:
#       print "Error inserting record into Plutora:", i, r.status_code
#       exit('Cant insert into Plutora')
#    else:
#       print('plSuystemCreate.py: too bad sucka! - [failed on POST]')

if __name__ == '__main__':
    # parse commandline and get appropriate passwords
    #    accepted format is python plSuystemCreate.py -f <config fiiename> -pusername:password
    #
    parser = argparse.ArgumentParser(description='Get user/password Plutora and configuration-filename.')
    #   help='JIRA and Plutora logins (username:password)')
    parser.add_argument('-f', action='store', dest='config_filename',
                        help='Config filename ')
    parser.add_argument('-p', action='store', dest='pltUnP',
                        help='Plutora username:password')
    results = parser.parse_args()

    config_filename = results.config_filename.split(':')[0]
    plutora_username = results.pltUnP.split(':')[0].replace('@', '%40')
    plutora_password = results.pltUnP.split(':')[1]

    # If we don't specify a configfile on the commandline, assume one & try accessing
    if len(config_filename) <= 0:
        config_filename = 'syscreate.cfg'

    # using the specified/assumed configfilename, grab ClientId & Secret from manual setup of Plutora Oauth authorization.
    try:
        with open(config_filename) as data_file:
            data = json.load(data_file)
        client_id = data["credentials"]["clientId"]
        client_secret = data["credentials"]["clientSecret"]
    except Exception,ex:
        # ex.msg is a string that looks like a dictionary
        print "EXCEPTION: %s " % ex.msg
        exit('couldnt open file {0}'.format(config_filename))

    createSystem(config_filename, client_id, client_secret, plutora_username, plutora_password)

    print("\n\nWell, it seems we're all done here, boys; time to pack up and go home...")

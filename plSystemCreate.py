#!/usr/bin/python

import requests
import pprint
import argparse
import json

#
# This is a sample program intended to demonstrate creating a system in Plutora
# it requires previously 'set up' access to Plutora (client_id and client_secret, etc)
#

# Set up JSON prettyPrinting
pp = pprint.PrettyPrinter(indent=4)

# parse commandline and get appropriate passwords
#    accepted format is python plSuystemCreate.py -f <config fiiename> -pusername:password
parser = argparse.ArgumentParser(description='Get user/password Plutora and configuration-filename.')
#   help='JIRA and Plutora logins (username:password)')
parser.add_argument('-f', action='store', dest='cfgFilename',
                    help='Config filename ')
parser.add_argument('-p', action='store', dest='pltUnP',
                    help='Plutora username:password')
results = parser.parse_args()

cfgFilename = results.cfgFilename.split(':')[0]
PlutoraUsername = results.pltUnP.split(':')[0].replace('@', '%40')
PlutoraPassword = results.pltUnP.split(':')[1]

if len(cfgFilename) <= 0:
    cfgFilename = 'syscreate.cfg'

# ClientId & Secret from manual setup of Plutora Oauth authorization.
#    read from configFile
try:
    with open(cfgFilename) as data_file:
        data = json.load(data_file)
    clientid = data["credentials"]["clientId"]
    clientsecret = data["credentials"]["clientSecret"]
except:
    exit('couldnt open file {0}',cfgFilename)



# Setup for Get authorization-token
authTokenUrl = "https://usoauth.plutora.com/oauth/token"
payload = 'client_id=' + clientid + '&client_secret=' + clientsecret + '&' + 'grant_type=password&username='
payload = payload + PlutoraUsername + '&password=' + PlutoraPassword + '&='
headers = {
    'content-type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache",
    'postman-token': "bc355474-15d1-1f56-6e35-371b930eac6f"
    }

# Connect to get Plutora access token for subsequent queries
authResponse = requests.post(authTokenUrl, data=payload, headers=headers)
if authResponse.status_code != 200:
    print(authResponse.status_code)
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
    'content-type': "application/x-www-form-urlencoded",
    'authorization': "bearer "+accessToken,
    'cache-control': "no-cache",
    'postman-token': "bc355474-15d1-1f56-6e35-371b930eac6f"
}

# Get Plutora information for all system releases
getReleases = '/releases/9d18a2dc-b694-4b20-971f-4944420f4038'
getSystems = '/systems'
getOrganizationsTree = '/organizations/tree'

r = requests.get(plutoraBaseUrl+getOrganizationsTree, data=payload, headers=headers)
if r.status_code != 200:
    print r.status_code
    print('\npltSystemCreate.py: too bad sucka! - [failed on Plutora get]')
    exit('Sorry, unrecoverable error; gotta go...')
else:
    print('\npltSystemCreate.py - Plutora get of organizations information:')
    pp.pprint(r.json())

fstChildsId = r.json()['childs'][0]['id']
#"additionalInformation":[],
payload = r"""{
  "Name": "API created System 1",
  "Vendor": "API created vendor",
  "Status": "Active",
  "OrganizationId": "%s",
  "Description": "Description of API created System 1"
}""" % r.json()['childs'][0]['id']

postSystem = '/systems'
print("Here's what I'm sending Plutora (headers & payload):")
print("header: ",headers)
print("payload: ",payload)

r = requests.post(plutoraBaseUrl+postSystem, data=payload, headers=headers)
if r.status_code != 200:
    print r.status_code
    print('\npltSystemCreate.py: too bad sucka! - [failed on Plutora create system POST]')
    pp.pprint(r.json())
    exit('Sorry, unrecoverable error; gotta go...')
else:
    print('\npltSystemCreate.py - Plutora POST of new system information:')
    pp.pprint(r.json())

print("\n\nWell, it seems we're all done here, boys")
#for i in r.json()["issues"]:
#    print("field is", i["fields"]["description"])
#    r = requests.post(plutoraMaerskUrl, data=i["fields"]["description"], headers=headers)
#    if r.status_code != 200:
#       print "Error inserting record into Plutora:", i, r.status_code
#       exit('Cant insert into Plutora')
#    else:
#       print('plSuystemCreate.py: too bad sucka! - [failed on POST]')
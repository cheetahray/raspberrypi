import requests
import json
import urllib
from socket import *
import sys
from threading import Thread
import time

#time.sleep(15)

PORT = 12345 # arbitrary, just make it match in Android code
IP = "" # represents any IP address

sock = socket(AF_INET, SOCK_DGRAM) # SOCK_DGRAM means UDP socket
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # make socket reuseable
sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
sock.bind((IP, PORT))
raytuple = ("192.168.11.255",PORT)

#Required header for XBMC JSON-RPC calls, otherwise you'll get a
#415 HTTP response code - Unsupported media type
headers = {'content-type': 'application/json'}

#Host name where XBMC is running, leave as localhost if on this PC
#Make sure "Allow control of XBMC via HTTP" is set to ON in Settings ->
#Services -> Webserver
xbmc_host = 'localhost'

#Configured in Settings -> Services -> Webserver -> Port
xbmc_port = 8080
xbmc_json_rpc_url = "http://" + xbmc_host + ":" + str(xbmc_port) + "/jsonrpc"

#Payload for the method to get the currently playing / paused video or audio
payload = {"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}
url_param = urllib.urlencode({'request': json.dumps(payload)})
rayget = xbmc_json_rpc_url + '?' + url_param

payload = {"jsonrpc": "2.0", "method": "Player.Open",
            #          "params": {"item":{"playlistid":1, "position" : 0}}, "id": 1}
            #          "params": { "item": { "file": "/home/pi/Palmipedarium_AVC_HD.mp4" }}, "id": 1}
                       "params": { "item": { "file": "/home/kodi/.kodi/userdata/playlists/video/1.m3u" }}, "id": 1}
raydata = json.dumps(payload)
#Base URL of the json RPC calls. For GET calls we append a "request" URI
#parameter. For POSTs, we add the payload as JSON the the HTTP request body
iam = ''
ishould = 'pl'
cntnow = 0
cntshould = 1
two = ''
twoshould = '2'
gettingclose = False
raydebug = True
rayspeed = 1
player_id = 0
def mystopfun():
    global rayspeed
    global raydebug
    global player_id
    if player_id > 0 and 1 == rayspeed:
        pauseload = {"jsonrpc":"2.0","method":"Player.PlayPause","params":{"playerid":player_id,"play":False},"id":1}
        response = requests.post(xbmc_json_rpc_url, json.dumps(pauseload), headers=headers)
        pausedata = json.loads(response.text)
        rayspeed = int(pausedata['result']["speed"])
        if True == raydebug:
            print response.text
        pauseload = { "id":1, "jsonrpc":"2.0", "method":"Player.Seek", "params": { "playerid":player_id, "value":0 }}
        response = requests.post(xbmc_json_rpc_url, json.dumps(pauseload), headers=headers)
        if True == raydebug:
            print response.text
        
def myspeedfun():
    global rayspeed
    global raydebug
    global ishould
    global raytuple
    global player_id
    if player_id > 0 and 0 == rayspeed:
        pauseload = {"jsonrpc":"2.0","method":"Player.PlayPause","params":{"playerid":player_id,"play":True},"id":1}
        response = requests.post(xbmc_json_rpc_url, json.dumps(pauseload), headers=headers)
        pausedata = json.loads(response.text)
        rayspeed = int(pausedata['result']["speed"])
        if True == raydebug:
            print response.text
        sent = sock.sendto(ishould, raytuple)

def myfunc():
    global player_id, rayspeed, cntnow
    global gettingclose
    global iam, two 
    global raydebug
    while True:

        if '' != iam:

            if 0 == player_id:
                time.sleep(0.2)

                response = requests.get(rayget, headers=headers)
                #response.text will look like this if something is playing
                #{"id":1,"jsonrpc":"2.0","result":[{"playerid":1,"type":"video"}]}
                #and if nothing is playing:
                #{"id":1,"jsonrpc":"2.0","result":[]}

                threaddata = json.loads(response.text)
                #result is an empty list if nothing is playing or paused.
                if True == raydebug:
                    print response.text
                if threaddata['result']:
                    #We need the specific "playerid" of the currently playing file in order
                    #to pause it
                    player_id = int(threaddata['result'][0]["playerid"])
                    mystopfun()
            else:
                time.sleep(2)

                proload = {"jsonrpc": "2.0", "method": "Player.GetProperties",
                           "params": { "playerid": player_id, "properties" : ["percentage"] }, "id": 1}
                response = requests.get(xbmc_json_rpc_url + '?' + urllib.urlencode({'request': json.dumps(proload)}),
                                        headers=headers)

                prodata = json.loads(response.text)
                if True == raydebug:
                    print response.text
                if prodata.has_key('result'):
                    rayfloat = float(prodata['result']["percentage"])
                    if rayfloat > 99.0:
                        repeatload = {"jsonrpc": "2.0", "method": "Player.SetRepeat", "params": { "playerid": player_id, "repeat": "all" }, "id": 1}
                        response = requests.post(xbmc_json_rpc_url, json.dumps(repeatload), headers=headers)
                        #repeatdata = json.loads(response.text)
                        if True == raydebug:
                            print response.text
                        gettingclose = True
                    elif True == gettingclose and rayfloat < 1.0:
                        cntnow = 0
                        gettingclose = False
                        two = ''
                        mystopfun()
        else:
            time.sleep(1)
try:
    tt = Thread(target=myfunc, args=())
    tt.start()

    while True:
        if True == raydebug:
            print "Waiting for data..."
        data, addr = sock.recvfrom(1024) # blocking
        if True == raydebug:
            print "received: " + data

        if data == twoshould:
            if two!=twoshould:
                two = data
                cntnow += 1    
            elif cntnow == cntshould:
                myspeedfun()     
        elif data == 'go':
            iam = '1'   
            if 0 == player_id:
                response = requests.post(xbmc_json_rpc_url, raydata, headers=headers)
                if True == raydebug:
                    print response.text
        elif data == 'no':
            iam = ''
            cntnow = 0
            gettingclose = False
            rayspeed = 1
            two = ''
            if player_id > 0:
                #We need the specific "playerid" of the currently playing file in order
                #to pause it
                rayload = {"jsonrpc": "2.0", "method": "Player.Stop", "params": {"playerid": player_id} }
                response = requests.post(xbmc_json_rpc_url, json.dumps(rayload), headers=headers)
                if True == raydebug:
                    print response.text
                player_id = 0

finally:
    if True == raydebug:
        print >>sys.stderr, 'closing socket'
    sock.close()



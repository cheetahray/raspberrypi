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
sock.bind((IP, PORT))

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

#counter = 1
#totalnum = 1
player_id = 0
#sendmsg = '1'
#recemsg = '2'

#Payload for the method to get the currently playing / paused video or audio
payload = {"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}
url_param = urllib.urlencode({'request': json.dumps(payload)})
rayget = xbmc_json_rpc_url + '?' + url_param 
 
payload = {"jsonrpc": "2.0", "method": "Player.Open",
            #          "params": {"item":{"playlistid":1, "position" : 0}}, "id": 1}
            #          "params": { "item": { "file": "/home/pi/Palmipedarium_AVC_HD.mp4" }}, "id": 1}
                       "params": { "item": { "file": "/home/kodi/.kodi/userdata/playlists/video/1.m3u" }}, "id": 1}
data = json.dumps(payload)
#Base URL of the json RPC calls. For GET calls we append a "request" URI
#parameter. For POSTs, we add the payload as JSON the the HTTP request body
            
def myfunc():
    while(totalnum > counter):

        time.sleep(2)

        response = requests.get(rayget, headers=headers)
        #response.text will look like this if something is playing
        #{"id":1,"jsonrpc":"2.0","result":[{"playerid":1,"type":"video"}]}
        #and if nothing is playing:
        #{"id":1,"jsonrpc":"2.0","result":[]}
 
        data = json.loads(response.text)
        #result is an empty list if nothing is playing or paused.

        if data['result']:
            #We need the specific "playerid" of the currently playing file in order
            #to pause it

            player_id = int(data['result'][0]["playerid"])

try:
    tt = Thread(target=myfunc, args=())
    tt.start()
        
    while True:
        print "Waiting for data..."
        data, addr = sock.recvfrom(1024) # blocking
        print "received: " + data

        if data == 'go':

            response = requests.post(xbmc_json_rpc_url, data, headers=headers)
            
            print response.text

        elif data == 'no':

            if player_id > 0:
                #We need the specific "playerid" of the currently playing file in order
                #to pause it

                rayload = {"jsonrpc": "2.0", "method": "Player.Stop", "params": {"playerid": player_id} }

                response = requests.post(xbmc_json_rpc_url, json.dumps(rayload), headers=headers)
                        
                print response.text

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()
    

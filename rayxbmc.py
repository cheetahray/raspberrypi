import requests
import json
import urllib
 
#Required header for XBMC JSON-RPC calls, otherwise you'll get a 
#415 HTTP response code - Unsupported media type
headers = {'content-type': 'application/json'}
 
#Host name where XBMC is running, leave as localhost if on this PC
#Make sure "Allow control of XBMC via HTTP" is set to ON in Settings -> 
#Services -> Webserver
xbmc_host = 'localhost'
 
#Configured in Settings -> Services -> Webserver -> Port
xbmc_port = 8080
 
#Base URL of the json RPC calls. For GET calls we append a "request" URI 
#parameter. For POSTs, we add the payload as JSON the the HTTP request body
xbmc_json_rpc_url = "http://" + xbmc_host + ":" + str(xbmc_port) + "/jsonrpc"
 
#Payload for the method to get the currently playing / paused video or audio
payload = {"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}
url_param = urllib.urlencode({'request': json.dumps(payload)})
 
response = requests.get(xbmc_json_rpc_url + '?' + url_param, 
                        headers=headers)
 
#response.text will look like this if something is playing
#{"id":1,"jsonrpc":"2.0","result":[{"playerid":1,"type":"video"}]}
#and if nothing is playing:
#{"id":1,"jsonrpc":"2.0","result":[]}
print response.text     
data = json.loads(response.text)
#result is an empty list if nothing is playing or paused. 
if data['result']:
    #We need the specific "playerid" of the currently playing file in order 
    #to pause it
    player_id = data['result'][0]["playerid"]
 
    payload = {"jsonrpc": "2.0", "method": "Player.PlayPause", 
               "params": { "playerid": player_id }, "id": 1}
    response = requests.post(xbmc_json_rpc_url, data=json.dumps(payload), 
                             headers=headers)
     
    #response.text will look like this if we're successful:
    #{"id":1,"jsonrpc":"2.0","result":{"speed":0}}
else
    payload = {"jsonrpc": "2.0", "method": "Player.Open", 
               "params": { "item": { "file": "/home/pi/Palmipedarium_AVC_HD.mp4" }}, "id": 1}
    response = requests.post(xbmc_json_rpc_url, data=json.dumps(payload), 
                             headers=headers)
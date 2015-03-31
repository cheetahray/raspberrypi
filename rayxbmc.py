import requests
import json
import urllib
import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('192.168.11.70', 52790)
print >>sys.stderr, 'starting up on %s port %s' % server_address
#sock.bind(server_address)
 
#Required header for XBMC JSON-RPC calls, otherwise you'll get a 
#415 HTTP response code - Unsupported media type
headers = {'content-type': 'application/json'}
 
#Host name where XBMC is running, leave as localhost if on this PC
#Make sure "Allow control of XBMC via HTTP" is set to ON in Settings -> 
#Services -> Webserver
xbmc_host = 'localhost'
 
#Configured in Settings -> Services -> Webserver -> Port
xbmc_port = 8080

counter = 1

sendmsg = '1'
recemsg = '2'
try:
    
    while 2 > counter:
        # Send data
        print >>sys.stderr, 'sending "%s"' % sendmsg
        sent = sock.sendto(sendmsg, server_address)
        # Receive response
        print >>sys.stderr, 'waiting to receive'
        data = sock.recvfrom(4096)
        print >>sys.stderr, 'received "%s"' % data
        if data == recemsg:
            counter += 1
        time.sleep(1)

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()
    
 
#Base URL of the json RPC calls. For GET calls we append a "request" URI 
#parameter. For POSTs, we add the payload as JSON the the HTTP request body
xbmc_json_rpc_url = "http://" + xbmc_host + ":" + str(xbmc_port) + "/jsonrpc"
 
payload = {"jsonrpc": "2.0", "method": "Player.Open", 
               "params": {"item":{"playlistid":1, "position" : 0}}, "id": 1}
#payload = {"jsonrpc": "2.0", "method": "Player.Open", 
#           "params": { "item": { "file": "/home/pi/Palmipedarium_AVC_HD.mp4" }}, "id": 1}
response = requests.post(xbmc_json_rpc_url, data=json.dumps(payload), 
                             headers=headers)

print response.text     

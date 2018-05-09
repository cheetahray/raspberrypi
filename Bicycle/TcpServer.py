import socket
import threading
import pyqrcode
import sys
import wand
from wand.image import Image
from wand.display import display

bind_ip = '0.0.0.0'
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(1)  # max backlog of connections

print 'Listening on {}:{}'.format(bind_ip, bind_port)

def renewQR(url):
    url = pyqrcode.create('http://uca.edu')
    #print(url.terminal())
    #url.svg(sys.stdout, scale=1)
    IMAGE = 'big-number.png'
    url.png(IMAGE,scale=6)
    with Image(filename=IMAGE) as img:
        display(img)


def handle_client_connection(client_socket):
    request = client_socket.recv(1024)
    print 'Received {}'.format(request)
    client_socket.send('ACK!')
    client_socket.close()

while False:
    client_sock, address = server.accept()
    print 'Accepted connection from {}:{}'.format(address[0], address[1])
    client_handler = threading.Thread(
        target=handle_client_connection,
        args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
    )
    client_handler.start()

renewQR("try")

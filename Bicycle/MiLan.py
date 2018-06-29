import socket
import threading
import pyqrcode
import sys
#import wand
#from wand.image import Image
#from wand.display import display
import RPi.GPIO as GPIO  
import time
from neopixel import *
#import argparse
import thread
import datetime
import epd2in7b
#import imagedata
from PIL import Image, ImageFont, ImageDraw, ImageOps  
  
COLORED = 1
UNCOLORED = 0

# LED strip configuration:
LED_COUNT      = 23      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

circleCNT = 0
frompos = 0
topos = 256
NOW = datetime.datetime.now()

GPIO.setmode(GPIO.BCM)  

# GPIO 23 & 17 set up as inputs, pulled up to avoid false detection.  
# Both ports are wired to connect to GND on button press.  
# So we'll be setting up falling edge detection for both  
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)  

bind_ip = '0.0.0.0'
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(1)  # max backlog of connections

print 'Listening on {}:{}'.format(bind_ip, bind_port)

def processImage(path):  
    
    # size = 1920, 1080  
    image1 = Image.new("RGB", (176, 264))  
    image2 = Image.open(path)  
  
    #image2 = image2.resize((1920, 872), )  
    # image.thumbnail(size)  
      
    #draw = ImageDraw.Draw(image1)  
  
    # use a truetype font  
    #font = ImageFont.truetype("arial.ttf", 50)  
  
    #draw.text((100, 20), content, font = font)  
    bw, bh = image1.size  
    lw, lh = image2.size  
  
    image1.paste(image2, ((bw - lw)/2, (bh - lh)/2))  
  
    #path = os.path.split(path)  
    # image3 = Image.composite(image1, image2, "L")  
    #newpath = os.path.join(dir, "composite").replace('\\', '/')  
      
    #if not os.path.exists(newpath):  
        #os.mkdir(newpath)  
  
    #_path = os.path.join(newpath, '%s%s'%(content, "_merge.jpg"))  
    #image1.save(_path.replace('\\', '/'), "JPEG")  
    image1.save(path, "PNG")  
    
    #print 'Process image %s'%content  

def renewQR(source):
    print source
    url = pyqrcode.create(source)
    #print(url.terminal())
    #url.svg(sys.stdout, scale=1)
    IMAGE = 'black.png'
    url.png(IMAGE,scale=3)
    #with Image(filename=IMAGE) as img:
        #display(img)
    # display images
    processImage(IMAGE)
    image = Image.open(IMAGE)
    frame_black = epd.get_frame_buffer(image)
    #inverted_image = ImageOps.invert(image)
    #inverted_image.save('new_name.png')  
    #frame_red = epd.get_frame_buffer(inverted_image)
    epd.display_frame(frame_black, frame_black)

def handle_client_connection(client_socket):
    global circleCNT
    request = client_socket.recv(64)
    print 'Received {}'.format(request)
    try:
        if request.startswith("Q:"):
            url = request[2:]
            renewQR(url)
            client_socket.send('num:Q\r\n')
            renewQR(url)
        elif request.startswith("C"):
            client_socket.send('num:'+str(circleCNT)+'\r\n')
        elif request.startswith("Z"):
            client_socket.send('num:'+str(circleCNT)+'\r\n')
            circleCNT = 0
            colorWipe(strip, Color(0,0,0), 10)
    except ValueError, e:
        print e
        pass
    #client_socket.close()

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def circlewheel(pos):
    return Color(0, 255-pos, pos)

def redblue(strip, wait_ms=1, iterations=1):
    global frompos, topos
    print frompos,topos
    if topos < frompos:
        iterations = -1
    for j in range(frompos,topos,iterations):
        for i in range(strip.numPixels()):
            if i< (circleCNT%strip.numPixels()):
                strip.setPixelColor(i, circlewheel(j) )
            else:
                strip.setPixelColor(i, Color(0,0,0) )
        strip.show()
        time.sleep(wait_ms/1000.0)
    frompos = topos-1

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def my_callback2(channel):
    global circleCNT
    global frompos,topos
    global NOW
    print "Bicycle Circle", circleCNT
    circleCNT+=1
    aa = (datetime.datetime.now() - NOW).total_seconds()*5
    if aa > 2.56:
        aa = 2.56
    topos = int(aa * 100) 
    NOW = datetime.datetime.now()
    thread.start_new_thread(redblue,(strip,4,1))

# when a falling edge is detected on port 23, regardless of whatever   
# else is happening in the program, the function my_callback2 will be run  
# 'bouncetime=300' includes the bounce control written into interrupts2a.py  
GPIO.add_event_detect(23, GPIO.FALLING, callback=my_callback2, bouncetime=300)  
  
# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

epd = epd2in7b.EPD()
epd.init()

# clear the frame buffer
frame_black = [0] * (epd.width * epd.height / 8)
frame_red = [0] * (epd.width * epd.height / 8)

try:  
    while True:
        '''
        print ('Color wipe animations.')
        colorWipe(strip, Color(255, 0, 0))  # Red wipe
        colorWipe(strip, Color(0, 255, 0))  # Blue wipe
        colorWipe(strip, Color(0, 0, 255))  # Green wipe
        print ('Theater chase animations.')
        theaterChase(strip, Color(127, 127, 127))  # White theater chase
        theaterChase(strip, Color(127,   0,   0))  # Red theater chase
        theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
        print ('Rainbow animations.')
        rainbow(strip)
        rainbowCycle(strip)
        theaterChaseRainbow(strip)
        '''
        client_sock, address = server.accept()
        print 'Accepted connection from {}:{}'.format(address[0], address[1])
        handle_client_connection(client_sock)
        '''
        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
        )
        client_handler.start()
        '''
except KeyboardInterrupt:  
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
    colorWipe(strip, Color(0,0,0), 10)


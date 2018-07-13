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
from sunrise_sunset import SunriseSunset  
from datetime import timedelta
from threading import Thread, Event, Timer
import commands 

COLORED = 1
UNCOLORED = 0

def TimerReset(*args, **kwargs):
    """ Global function for Timer """
    return _TimerReset(*args, **kwargs)


class _TimerReset(Thread):
    """Call a function after a specified number of seconds:

    t = TimerReset(30.0, f, args=[], kwargs={})
    t.start()
    t.cancel() # stop the timer's action if it's still waiting
    """

    def __init__(self, interval, function, args=[], kwargs={}):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()
        self.resetted = True
        self.debug = False
    def cancel(self):
        """Stop the timer if it hasn't finished yet"""
        self.finished.set()

    def run(self):
        if self.debug:
            print "Time: %s - timer running..." % time.asctime()

        while self.resetted:
            if self.debug:
                print "Time: %s - timer waiting for timeout in %.2f..." % (time.asctime(), self.interval)
            self.resetted = False
            self.finished.wait(self.interval)

        if not self.finished.isSet():
            self.function(*self.args, **self.kwargs)
        self.finished.set()
        if self.debug:
            print "Time: %s - timer finished!" % time.asctime()

    def reset(self, interval=None):
        """ Reset the timer """

        if interval:
            if self.debug:
                print "Time: %s - timer resetting to %.2f..." % (time.asctime(), interval)
            self.interval = interval
        else:
            if self.debug:
                print "Time: %s - timer resetting..." % time.asctime()

        self.resetted = True
        self.finished.set()
        self.finished.clear()

# LED strip configuration:
LED_COUNT      = 23      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 78     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
sensorCNT = 0
circleCNT = 0
LastcircleCNT = 0
frompos = 0
topos = 256
NOW = datetime.datetime.now()
rise_time = None
set_time = None
StartTime = NOW + timedelta(days=-1)
GPIO.setmode(GPIO.BCM)  

# GPIO 23 & 17 set up as inputs, pulled up to avoid false detection.  
# Both ports are wired to connect to GND on button press.  
# So we'll be setting up falling edge detection for both  
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)  

bind_ip = '0.0.0.0'
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(2)  # max backlog of connections

print 'Listening on {}:{}'.format(bind_ip, bind_port)

def processImage(path):  
    global whoami
    # size = 1920, 1080  
    image1 = Image.new("RGB", (176, 264))  
    image2 = Image.open(path)  
  
    #image2 = image2.resize((1920, 872), )  
    # image.thumbnail(size)  
      
    draw = ImageDraw.Draw(image1)  
    #draw.rectangle([(0,0),(176,50)], fill = (255,255,255)) 
    # use a truetype font  
    font = ImageFont.truetype("Arial.ttf", 50)  
  
    draw.text((60, 10), whoami, font = font)  
    draw.text((60, 200), whoami, font = font)
    bw, bh = image1.size  
    lw, lh = image2.size  
  
    image1.paste(image2, ((bw - lw)/2, (bh - lh)/2))  
  
    #path = os.path.split(path)  
    # image3 = Image.composite(image1, image2, "L")  
    #newpath = os.path.join(dir, "composite").replace('\\', '/')  
      
    #if not os.path.exists(newpath):  
        #os.mkdir(newpath)  
    image1 = image1.transpose( Image.ROTATE_180 )
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
    global circleCNT,sensorCNT, LastcircleCNT
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
            LastcircleCNT = 0
            sensorCNT = 0
            colorWipe(strip, Color(0,0,0), 10)
        elif request.startswith("J"):
            for ii in range(0, LED_BRIGHTNESS, 3):
                colorWipe(strip, Color(0,127,127), 0, ii) 
                time.sleep(0.001)
            for ii in range(LED_BRIGHTNESS, -1, -3):
                colorWipe(strip, Color(0,127,127), 0, ii)
                time.sleep(0.001)
            client_socket.send('num:J\r\n')
    except ValueError, e:
        print e
        pass
    #client_socket.close()

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50, brightness=256):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        if brightness < 256:
            strip.setBrightness(brightness)
        strip.show()
        if wait_ms != 0:
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

def tensec(idx,idx2):
    renewQR(idx)

HIGHLOW = 0
def my_callback(channel):
    global HIGHLOW
    if GPIO.input(23):     # if port 25 == 1
        if HIGHLOW == 0:
            HIGHLOW = 1
        print "Rising"
    else:                  # if port 25 != 1
        if HIGHLOW == 1:
            HIGHLOW = 0
            my_callback2(channel)            
        print "Falling"

def my_callback2(channel):
    global circleCNT,sensorCNT,LastcircleCNT
    global frompos,topos
    global NOW, rise_time, set_time
    global UU
    print "Bicycle Circle", circleCNT
    sensorCNT+=1
    circleCNT=sensorCNT/5
    if circleCNT != LastcircleCNT:
        UU.reset()
        LastcircleCNT = circleCNT
        aa = (datetime.datetime.now() - NOW).total_seconds() * 2.25
        if aa > 2.56:
            aa = 2.56
        topos = int(aa * 100) 
        NOW = datetime.datetime.now()
        '''
        print rise_time, set_time
        if NOW > rise_time and NOW < set_time:
            strip.setbrightness(255)
        else:
            strip.setbrightness(200)
        '''
        thread.start_new_thread(redblue,(strip,4,1))

def calrisesettime():
    global NOW, rise_time, set_time
    ro = SunriseSunset(NOW, longitude=121.535844, latitude=25.033303, localOffset=8)
    rise_time, set_time = ro.calculate()

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

epd = epd2in7b.EPD()
epd.init()

# clear the frame buffer
frame_black = [0] * (epd.width * epd.height / 8)
frame_red = [0] * (epd.width * epd.height / 8)
TT = TimerReset(30, tensec, ("https://ecogym.taipei/app.html#/device-error","https://ecogym.taipei/app.html#/device-error"))
UU = TimerReset(20, colorWipe, (strip, Color(0, 0, 0),10) )

# when a falling edge is detected on port 23, regardless of whatever   
# else is happening in the program, the function my_callback2 will be run  
# 'bouncetime=300' includes the bounce control written into interrupts2a.py  
GPIO.add_event_detect(23, GPIO.BOTH, callback=my_callback)#2, bouncetime=300)  

ips = commands.getoutput("/sbin/ifconfig | grep -iA2 \"eth0\" | grep -i \"inet\" | grep -iv \"inet6\" | " +
                         "awk {'print $2'} ") #| sed -ne 's/addr\://p'")
iplist = ips.split(".")
whoami = iplist[3]
  
try:  
    TT.start()
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
        if StartTime.day != NOW.day:
            StartTime = datetime.datetime.now()
            calrisesettime()
        client_sock, address = server.accept()
        TT.reset()
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
    TT.cancel()
    UU.cancel()

#!/usr/bin/python

import RPi.GPIO as GPIO
import time

BTN_PIN = 11
BOUNCE_TIME = 200
GPIO.setup(BTN_PIN, GPIO.IN,pull_up_down=GPIO.PUD_UP)
def callback_function(channel):
    print("Button.Click"), strftime("%Y-%m-%d %H:%M:%S", gmtime())
try:
    GPIO.add_event_detect(BTN_PIN, GPIO.FALLING,callback=callback_function, bouncetime=BOUNCE_TIME)
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    GPIO.cleanup()
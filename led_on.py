#!/usr/bin/python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
BTN_PIN = 11
GPIO.setup(BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
try :
    while True:
        if GPIO.input(BTN_PIN) == GPIO.LOW :
            print("Button.Click")

except KeyboardInterrupt:
    GPIO.cleanup()
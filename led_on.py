#!/usr/bin/python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
LED_PIN = 12
GPIO.setup(LED_PIN, GPIO.OUT)

print("LED is on")
GPIO.output(LED_PIN, GPIO.HIGH)
time.sleep(3)

GPIO.cleanup()

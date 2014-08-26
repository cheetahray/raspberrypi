import pygame
import pygame.camera

pygame.init()
pygame.camera.init()
from pygame.locals import *

scale = 0.8
miwidth = 1920
miheight = 1080 
size = ((miwidth, miheight))

display = pygame.display.set_mode(size,0)

cam = pygame.camera.Camera("/dev/video0", size)
cam.start()

while True:
    #mimiwidth = 1280
    #mimiheight = 720
    image = cam.get_image()
    #mimiwidth = int(mimiwidth * scale)
    #mimiheight = int(mimiheight * scale)
    #lines = pygame.transform.scale(image, (mimiwidth, mimiheight))
    display.blit(image, (0,0))
    #display.blit(lines, ((miwidth-mimiwidth)/2,(miheight-mimiheight)/2))
    pygame.display.flip()


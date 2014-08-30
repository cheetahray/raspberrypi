import pygame
import pygame.camera

pygame.init()
pygame.camera.init()

w = 960;
h = 720;
display = pygame.display.set_mode((w,h),0)
pygame.mouse.set_visible(False)
cam = pygame.camera.Camera("/dev/video0", (w,h))
cam.start()

while True:
    image = cam.get_image()
    display.blit(image, (0,0))
    pygame.display.flip()

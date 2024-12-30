import pygame

# --- constants --- (UPPER_CASE names)

SCREEN_WIDTH = 430
SCREEN_HEIGHT = 410

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)

FPS = 60

# --- classses --- (CamelCase names)

# empty

# --- functions --- (lower_case names)

# empty

# --- main ---

# - init -

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
#screen_rect = screen.get_rect()

pygame.display.set_caption("Tracking System")

# - objects -

circle = pygame.rect.Rect(176, 134, 30, 30)
circle_draging = False

# - mainloop -

clock = pygame.time.Clock()

running = True

while running:

    # - events -

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:            
                if circle.collidepoint(event.pos):
                    circle_draging = True
                    mouse_x, mouse_y = event.pos
                    offset_x = circle.x - mouse_x
                    offset_y = circle.y - mouse_y

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:            
                circle_draging = False

        elif event.type == pygame.MOUSEMOTION:
            if circle_draging:
                mouse_x, mouse_y = event.pos
                circle.x = mouse_x + offset_x
                circle.y = mouse_y + offset_y

    # - updates (without draws) -

    # empty

    # - draws (without updates) -

    screen.fill(WHITE)

    pygame.draw.circle(screen, BLACK, circle.center, circle.width//2)

    pygame.display.flip()

    # - constant game speed / FPS -

    clock.tick(FPS)

# - end -

pygame.quit()
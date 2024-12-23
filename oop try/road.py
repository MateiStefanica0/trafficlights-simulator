import pygame

class Road:
    def __init__(self, screen, position, size=(100, 5), color=(0, 0, 0)):
        self.screen = screen
        self.position = position
        self.size = size
        self.color = color
        self.dragging = False
        self.rotation = 0

    def draw(self):
        rect = pygame.Surface(self.size, pygame.SRCALPHA)
        rect.fill(self.color)
        rotated_rect = pygame.transform.rotate(rect, self.rotation)
        rect_center = rotated_rect.get_rect(center=self.position)
        self.screen.blit(rotated_rect, rect_center.topleft)

    def rotate(self, angle):
        self.rotation = (self.rotation + angle) % 360

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_mouse_on_road(event.pos):
                self.dragging = True
                self.mouse_offset = (self.position[0] - event.pos[0], self.position[1] - event.pos[1])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.position = (event.pos[0] + self.mouse_offset[0], event.pos[1] + self.mouse_offset[1])

    def is_mouse_on_road(self, mouse_pos):
        x, y = self.position
        width, height = self.size
        rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
        return rect.collidepoint(mouse_pos)
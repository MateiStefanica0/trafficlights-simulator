import pygame

class Intersection:
    def __init__(self, screen, position, radius=10, color=(0, 0, 0)):
        self.screen = screen
        self.position = position
        self.radius = radius
        self.color = color
        self.dragging = False
        self.draw()

    def draw(self):
        pygame.draw.circle(self.screen, self.color, self.position, self.radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_mouse_on_intersection(event.pos):
                self.dragging = True
                self.mouse_offset = (self.position[0] - event.pos[0], self.position[1] - event.pos[1])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.position = (event.pos[0] + self.mouse_offset[0], event.pos[1] + self.mouse_offset[1])

    def is_mouse_on_intersection(self, mouse_pos):
        distance = ((self.position[0] - mouse_pos[0]) ** 2 + (self.position[1] - mouse_pos[1]) ** 2) ** 0.5
        return distance <= self.radius
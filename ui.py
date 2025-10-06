from settings import *

import pygame

class DrawGrid: #might change name later
    def __init__(self):
        self.buttons = []
        self.active_tool = 1
        self.font = pygame.font.SysFont("Arial", 18)
        self.create_button("T1", 10, 20, 180, 40, 1)
        self.create_button("T2", 10, 70, 180, 40, 2)
    
    def create_button(self, label, x, y, w, h, tool_id):
        rect = pygame.Rect(GRID_WIDTH * TILE_SIZE + x, y, w, h)
        self.buttons.append({"rect": rect, "label": label, "tool": tool_id})

    def draw(self, screen):
        pygame.draw.rect(screen, BGC, (GRID_WIDTH * TILE_SIZE, 0, 200, SCREEN_HEIGHT))

        for b in self.buttons:
            colour = (100, 100, 100)

            if b["tool"] == self.active_tool:
                colour = (150, 150, 150)

            pygame.draw.rect(screen, colour, b["rect"], border_radius=6)
            text = self.font.render(b["label"], True, WHITE)
            screen.blit(text, (b["rect"].x + 10, b["rect"].y + 10))

    def handle_click(self, pos):
        for b in self.buttons:
            if b["rect"].collidepoint(pos):
                self.active_tool = b["tool"]

    def get_active_tool(self):
        return self.active_tool
from settings import *

import pygame

class DrawGrid:
    def __init__(self):
        self.buttons = []
        self.active_tool = 1
        self.font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 14)
        self.money_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.create_button("Pipe", 10, 80, 180, 40, 1)
        self.create_button("Drill", 10, 130, 180, 40, 2)
        self.create_button("Van Depot", 10, 180, 180, 40, 3)
        self.create_button("Delete", 10, 230, 180, 40, 0)
        self.selected_tile = None
        self.info_panel_rect = None

    def create_button(self, label, x, y, w, h, tool_id):
        rect = pygame.Rect(SCREEN_WIDTH - SIDEBAR_WIDTH + x, y, w, h)
        self.buttons.append({"rect": rect, "label": label, "tool": tool_id})

    def draw(self, screen, money):
        sidebar_x = SCREEN_WIDTH - SIDEBAR_WIDTH
        pygame.draw.rect(screen, (40, 40, 40), (sidebar_x, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
        money_panel_rect = pygame.Rect(sidebar_x + 10, 10, 180, 60)
        pygame.draw.rect(screen, (30, 80, 30), money_panel_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 200, 100), money_panel_rect, 2, border_radius=8)
        money_label = self.small_font.render("Total Capital", True, (150, 255, 150))
        screen.blit(money_label, (sidebar_x + 20, 18))
        money_text = self.money_font.render(f"${money:,.2f}", True, (200, 255, 200))
        screen.blit(money_text, (sidebar_x + 20, 38))
        for b in self.buttons:
            if b["label"] != "Delete":
                colour = (100, 100, 100)
                if b["tool"] == self.active_tool:
                    colour = (150, 150, 150)
                pygame.draw.rect(screen, colour, b["rect"], border_radius=6)
                text = self.font.render(b["label"], True, WHITE)
                screen.blit(text, (b["rect"].x + 10, b["rect"].y + 10))
            else:
                colour = (200, 0, 0)
                if b["tool"] == self.active_tool:
                    colour = (255, 0, 0)
                pygame.draw.rect(screen, colour, b["rect"], border_radius=6)
                text = self.font.render(b["label"], True, WHITE)
                screen.blit(text, (b["rect"].x + 10, b["rect"].y + 10))
        if self.selected_tile:
            self.draw_info_panel(screen)

    def draw_info_panel(self, screen):
        tile_data, gx, gy = self.selected_tile
        tile_type = tile_data["type"]
        if tile_type == 0:
            return
        panel_width = 180
        panel_height = 250
        panel_x = SCREEN_WIDTH - SIDEBAR_WIDTH + 10
        panel_y = 290
        self.info_panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (40, 40, 40), self.info_panel_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 100), self.info_panel_rect, 2, border_radius=8)
        machine_info = MACHINE_STATS.get(tile_type, {})
        machine_name = machine_info.get("name", "Unknown")
        y_offset = panel_y + 10
        title_text = self.font.render(machine_name, True, (255, 255, 100))
        screen.blit(title_text, (panel_x + 10, y_offset))
        y_offset += 30
        tier_text = self.small_font.render("Tier: I", True, (200, 200, 200))
        screen.blit(tier_text, (panel_x + 10, y_offset))
        y_offset += 25
        pos_text = self.small_font.render(f"Position: ({gx}, {gy})", True, (150, 150, 150))
        screen.blit(pos_text, (panel_x + 10, y_offset))
        y_offset += 25
        stored_item = tile_data.get("stored", None)
        amount = tile_data.get("amount", 0)
        
        if tile_type == 1:
            capacity = machine_info.get("capacity", 10)
            storage_text = self.small_font.render("Storage:", True, WHITE)
            screen.blit(storage_text, (panel_x + 10, y_offset))
            y_offset += 20
            
            item_text = f"{stored_item or 'Empty'}: {amount}/{capacity}"
            item_render = self.small_font.render(item_text, True, (180, 180, 255))
            screen.blit(item_render, (panel_x + 15, y_offset))
            y_offset += 25
            
            if stored_item and amount > 0:
                item_value = ITEM_VALUES.get(stored_item, 0)
                total_value = amount * item_value
                value_text = self.small_font.render(f"Value: ${total_value:,.2f}", True, (150, 255, 150))
                screen.blit(value_text, (panel_x + 15, y_offset))
                y_offset += 20
            
        elif tile_type == 2:
            storage_text = self.small_font.render("Storage:", True, WHITE)
            screen.blit(storage_text, (panel_x + 10, y_offset))
            y_offset += 20
            
            item_text = f"{stored_item or 'Empty'}: {amount}"
            item_render = self.small_font.render(item_text, True, (255, 200, 100))
            screen.blit(item_render, (panel_x + 15, y_offset))
            y_offset += 25
            
            if stored_item and amount > 0:
                item_value = ITEM_VALUES.get(stored_item, 0)
                total_value = amount * item_value
                value_text = self.small_font.render(f"Value: ${total_value:,.2f}", True, (150, 255, 150))
                screen.blit(value_text, (panel_x + 15, y_offset))
                y_offset += 20
            progress_text = self.small_font.render("Production:", True, WHITE)
            screen.blit(progress_text, (panel_x + 10, y_offset))
            y_offset += 20

            #Bar params
            bar_width = 160
            bar_height = 15
            bar_x = panel_x + 10
            bar_y = y_offset
            pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=3)
            timer = tile_data.get("timer", 0)
            production_time = 2.0
            progress = min(timer / production_time, 1.0)
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, fill_width, bar_height), border_radius=3)
            percent_text = self.small_font.render(f"{int(progress * 100)}%", True, WHITE)
            screen.blit(percent_text, (bar_x + bar_width // 2 - 15, bar_y + 1))
            y_offset += 20
        elif tile_type == 3:
            capacity = machine_info.get("capacity", 20)
            storage_text = self.small_font.render("Storage:", True, WHITE)
            screen.blit(storage_text, (panel_x + 10, y_offset))
            y_offset += 20
            item_text = f"{stored_item or 'Empty'}: {amount}/{capacity}"
            item_render = self.small_font.render(item_text, True, (150, 255, 150))
            screen.blit(item_render, (panel_x + 15, y_offset))
            y_offset += 25
            if stored_item and amount > 0:
                item_value = ITEM_VALUES.get(stored_item, 0)
                current_value = amount * item_value
                value_text = self.small_font.render(f"Current: ${current_value:,.2f}", True, (200, 200, 100))
                screen.blit(value_text, (panel_x + 15, y_offset))
                y_offset += 20
                if amount >= capacity:
                    sale_value = capacity * item_value
                    sale_text = self.small_font.render(f"Sale: ${sale_value:,.2f}", True, (100, 255, 100))
                    screen.blit(sale_text, (panel_x + 15, y_offset))
                    y_offset += 5
            y_offset += 5
            if amount >= capacity and stored_item:
                status_text = self.small_font.render("Status: READY!", True, (255, 255, 100))
            elif amount > 0:
                status_text = self.small_font.render("Status: Collecting...", True, (150, 150, 255))
            else:
                status_text = self.small_font.render("Status: Waiting", True, (150, 150, 150))
            screen.blit(status_text, (panel_x + 10, y_offset))
            y_offset += 25
            total_sold = tile_data.get("total_sold", 0)
            sold_text = self.small_font.render(f"Total Sold: {total_sold} units", True, (100, 255, 100))
            screen.blit(sold_text, (panel_x + 10, y_offset))

    def handle_click(self, pos):
        for b in self.buttons:
            if b["rect"].collidepoint(pos):
                self.active_tool = b["tool"]
                return True
        return False
    
    def handle_tile_click(self, grid, gx, gy):
        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
            tile_data = grid[gy][gx]
            self.selected_tile = (tile_data, gx, gy)

    def get_active_tool(self):
        return self.active_tool
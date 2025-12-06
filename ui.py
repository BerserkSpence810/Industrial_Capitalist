from settings import *

import pygame

class DrawGrid:
    def __init__(self):
        self.buttons = []
        self.active_tool = -1  #Start Inspect)
        self.font = pygame.font.SysFont("Arial", 16)
        self.small_font = pygame.font.SysFont("Arial", 13)
        self.tiny_font = pygame.font.SysFont("Arial", 11)
        self.money_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 14, bold=True)
        
        self.create_button("Pipe", 10, 80, 180, 50, 1)
        self.create_button("Coal Drill", 10, 140, 180, 50, 2)
        self.create_button("Van Depot", 10, 200, 180, 50, 3)
        self.create_button("Delete", 10, 260, 180, 50, 0)
        
        self.selected_tile = None
        self.info_panel_rect = None
        
        #Transaction message system
        self.transaction_message = None
        self.transaction_timer = 0
        self.transaction_duration = 1.5 #Time

    def create_button(self, label, x, y, w, h, tool_id):
        rect = pygame.Rect(SCREEN_WIDTH - SIDEBAR_WIDTH + x, y, w, h)
        self.buttons.append({"rect": rect, "label": label, "tool": tool_id})

    def show_transaction_message(self, message, color):
        self.transaction_message = message
        self.transaction_color = color
        self.transaction_timer = self.transaction_duration

    def draw(self, screen, money):
        sidebar_x = SCREEN_WIDTH - SIDEBAR_WIDTH
        pygame.draw.rect(screen, (40, 40, 40), (sidebar_x, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
        
        #Money panel
        money_panel_rect = pygame.Rect(sidebar_x + 10, 10, 180, 55)
        pygame.draw.rect(screen, (35, 35, 35), money_panel_rect, border_radius=5)
        pygame.draw.rect(screen, (80, 80, 80), money_panel_rect, 1, border_radius=5)
        
        money_label = self.tiny_font.render("CAPITAL", True, (120, 120, 120))
        screen.blit(money_label, (sidebar_x + 20, 18))
        money_text = self.money_font.render(f"${money:,.2f}", True, (100, 255, 100))
        screen.blit(money_text, (sidebar_x + 20, 35))
        
        #Transaction message
        if self.transaction_timer > 0:
            alpha_factor = self.transaction_timer / self.transaction_duration
            msg_surface = self.font.render(self.transaction_message, True, self.transaction_color)
            msg_y = 75 - int((1 - alpha_factor) * 10)  # Float upward
            msg_rect = msg_surface.get_rect(center=(sidebar_x + 100, msg_y))
            screen.blit(msg_surface, msg_rect)
            self.transaction_timer -= clock.get_time() / 1000
        
        #Buttons
        for b in self.buttons:
            machine_cost = MACHINE_STATS.get(b["tool"], {}).get("cost", 0)
            is_selected = b["tool"] == self.active_tool
            
            if b["label"] == "Delete":
                #Delete button
                base_color = (80, 30, 30) if not is_selected else (120, 40, 40)
                border_color = (150, 50, 50) if is_selected else (100, 40, 40)
            else:
                #Normal buttons
                base_color = (55, 55, 55) if not is_selected else (70, 70, 70)
                border_color = (100, 100, 100) if is_selected else (70, 70, 70)
            
            #Draw button
            pygame.draw.rect(screen, base_color, b["rect"], border_radius=4)
            pygame.draw.rect(screen, border_color, b["rect"], 2 if is_selected else 1, border_radius=4)
            
            #Button label
            text_color = WHITE if is_selected else (200, 200, 200)
            text = self.font.render(b["label"], True, text_color)
            screen.blit(text, (b["rect"].x + 10, b["rect"].y + 8))
            
            #Show cost/refund info
            if b["label"] == "Delete":
                refund_text = self.small_font.render("Refund: 80%", True, (180, 120, 120))
                screen.blit(refund_text, (b["rect"].x + 10, b["rect"].y + 28))
            else:
                cost_color = (100, 255, 100) if machine_cost <= money else (255, 100, 100)
                cost_text = self.small_font.render(f"Cost: ${machine_cost}", True, cost_color)
                screen.blit(cost_text, (b["rect"].x + 10, b["rect"].y + 28))
        
        #Info panel
        if self.selected_tile:
            self.draw_info_panel(screen)

    def draw_info_panel(self, screen):
        tile_data, gx, gy = self.selected_tile
        tile_type = tile_data["type"]
        if tile_type == 0:
            return
            
        panel_width = 180
        panel_height = 270
        panel_x = SCREEN_WIDTH - SIDEBAR_WIDTH + 10
        panel_y = 325
        
        self.info_panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (35, 35, 35), self.info_panel_rect, border_radius=5)
        pygame.draw.rect(screen, (80, 80, 80), self.info_panel_rect, 1, border_radius=5)
        
        machine_info = MACHINE_STATS.get(tile_type, {})
        machine_name = machine_info.get("name", "Unknown")
        machine_cost = machine_info.get("cost", 0)
        
        y_offset = panel_y + 10
        
        #Title
        title_text = self.title_font.render(machine_name, True, (255, 220, 100))
        screen.blit(title_text, (panel_x + 10, y_offset))
        y_offset += 22
        
        #Separator line
        pygame.draw.line(screen, (60, 60, 60), (panel_x + 10, y_offset), (panel_x + panel_width - 10, y_offset), 1)
        y_offset += 8
        
        #Position
        pos_text = self.small_font.render(f"Pos: ({gx}, {gy}) | Tier I", True, (140, 140, 140))
        screen.blit(pos_text, (panel_x + 10, y_offset))
        y_offset += 20
        
        #Value info
        sell_value = machine_cost * 0.8
        value_text = self.small_font.render(f"Value: ${machine_cost}  Sell: ${sell_value:.0f}", True, (180, 180, 180))
        screen.blit(value_text, (panel_x + 10, y_offset))
        y_offset += 25
        
        stored_item = tile_data.get("stored", None)
        amount = tile_data.get("amount", 0)
        
        #Storage section header
        storage_header = self.title_font.render("STORAGE", True, (200, 200, 200))
        screen.blit(storage_header, (panel_x + 10, y_offset))
        y_offset += 20
        
        if tile_type == 1:  #Pipe
            capacity = machine_info.get("capacity", 10)
            item_text = f"{stored_item or 'Empty'}: {amount}/{capacity}"
            item_render = self.small_font.render(item_text, True, (150, 180, 255))
            screen.blit(item_render, (panel_x + 15, y_offset))
            y_offset += 20
            
            if stored_item and amount > 0:
                item_value = ITEM_VALUES.get(stored_item, 0)
                total_value = amount * item_value
                value_text = self.small_font.render(f"Worth: ${total_value:,.2f}", True, (120, 220, 120))
                screen.blit(value_text, (panel_x + 15, y_offset))
            
        elif tile_type == 2:  #Coal Drill
            item_text = f"{stored_item or 'Empty'}: {amount}"
            item_render = self.small_font.render(item_text, True, (255, 200, 120))
            screen.blit(item_render, (panel_x + 15, y_offset))
            y_offset += 20
            
            if stored_item and amount > 0:
                item_value = ITEM_VALUES.get(stored_item, 0)
                total_value = amount * item_value
                value_text = self.small_font.render(f"Worth: ${total_value:,.2f}", True, (120, 220, 120))
                screen.blit(value_text, (panel_x + 15, y_offset))
                y_offset += 20
            
            y_offset += 10
            progress_text = self.title_font.render("PRODUCTION", True, (200, 200, 200))
            screen.blit(progress_text, (panel_x + 10, y_offset))
            y_offset += 20

            #Progress bar
            bar_width = 160
            bar_height = 12
            bar_x = panel_x + 10
            bar_y = y_offset
            
            pygame.draw.rect(screen, (25, 25, 25), (bar_x, bar_y, bar_width, bar_height), border_radius=3)
            pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), 1, border_radius=3)
            
            timer = tile_data.get("timer", 0)
            production_time = 2.0
            progress = min(timer / production_time, 1.0)
            fill_width = int(bar_width * progress)
            
            if fill_width > 0:
                pygame.draw.rect(screen, (80, 200, 80), (bar_x, bar_y, fill_width, bar_height), border_radius=3)
            
            percent_text = self.tiny_font.render(f"{int(progress * 100)}%", True, WHITE)
            screen.blit(percent_text, (bar_x + bar_width // 2 - 12, bar_y + 2))
            
        elif tile_type == 3:  #Van Depot
            capacity = machine_info.get("capacity", 20)
            item_text = f"{stored_item or 'Empty'}: {amount}/{capacity}"
            item_render = self.small_font.render(item_text, True, (150, 255, 150))
            screen.blit(item_render, (panel_x + 15, y_offset))
            y_offset += 20
            
            if stored_item and amount > 0:
                item_value = ITEM_VALUES.get(stored_item, 0)
                current_value = amount * item_value
                value_text = self.small_font.render(f"Current: ${current_value:,.2f}", True, (200, 200, 120))
                screen.blit(value_text, (panel_x + 15, y_offset))
                y_offset += 18
                
                if amount >= capacity:
                    sale_value = capacity * item_value
                    sale_text = self.small_font.render(f"Ready to Ship: ${sale_value:,.2f}", True, (120, 255, 120))
                    screen.blit(sale_text, (panel_x + 15, y_offset))
                    y_offset += 5
            
            y_offset += 15
            
            #Status
            if amount >= capacity and stored_item:
                status_text = self.small_font.render("● SHIPPING", True, (100, 255, 100))
            elif amount > 0:
                status_text = self.small_font.render("● Collecting...", True, (150, 180, 255))
            else:
                status_text = self.small_font.render("● Idle", True, (120, 120, 120))
            screen.blit(status_text, (panel_x + 10, y_offset))
            y_offset += 25
            
            #total
            total_sold = tile_data.get("total_sold", 0)
            sold_text = self.small_font.render(f"Total Shipped: {total_sold} units", True, (140, 140, 140))
            screen.blit(sold_text, (panel_x + 10, y_offset))

    def handle_click(self, pos):
        for b in self.buttons:
            if b["rect"].collidepoint(pos):
                if self.active_tool == b["tool"]:
                    self.active_tool = -1
                else:
                    self.active_tool = b["tool"]
                return True
        return False
    
    def handle_tile_click(self, grid, gx, gy):
        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
            tile_data = grid[gy][gx]
            self.selected_tile = (tile_data, gx, gy)

    def get_active_tool(self):
        return self.active_tool
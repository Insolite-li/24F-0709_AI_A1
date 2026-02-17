"""
GUI Visualization Module using Pygame - ENHANCED VERSION
Handles all rendering and user interface with modern design
"""
import pygame
from typing import Tuple, List, Optional, Dict, Any
from grid import Grid
from config import *

# Initialize pygame
pygame.init()

class Visualizer:
    """
    Pygame-based visualizer for the pathfinding algorithms - Enhanced version
    """
    
    def __init__(self, grid: Grid):
        self.grid = grid
        
        # Calculate window dimensions
        self.grid_pixel_size = grid.size * CELL_SIZE
        self.sidebar_width = 300
        self.control_height = 100
        
        # Create window
        self.screen = pygame.display.set_mode((
            self.grid_pixel_size + self.sidebar_width,
            self.grid_pixel_size + self.control_height
        ))
        pygame.display.set_caption(WINDOW_TITLE)
        
        # Fonts - Try to use better fonts if available
        try:
            self.font_small = pygame.font.SysFont('Segoe UI', FONT_SIZE_SMALL)
            self.font_medium = pygame.font.SysFont('Segoe UI', FONT_SIZE_MEDIUM)
            self.font_large = pygame.font.SysFont('Segoe UI', FONT_SIZE_LARGE)
            self.font_title = pygame.font.SysFont('Segoe UI', FONT_SIZE_TITLE, bold=True)
        except:
            self.font_small = pygame.font.SysFont('Arial', FONT_SIZE_SMALL)
            self.font_medium = pygame.font.SysFont('Arial', FONT_SIZE_MEDIUM)
            self.font_large = pygame.font.SysFont('Arial', FONT_SIZE_LARGE)
            self.font_title = pygame.font.SysFont('Arial', FONT_SIZE_TITLE, bold=True)
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
        
        # Animation state
        self.animation_step = 0
        self.is_animating = False
        self.animation_delay = ANIMATION_DELAY
        
        # Buttons
        self.buttons = self._create_buttons()
        
        # Tooltip system
        self.tooltip_text = ""
        self.tooltip_pos = (0, 0)
        self.show_tooltip = False
        
        # Message system
        self.message = ""
        self.message_timer = 0
        self.message_duration = 3000  # 3 seconds
        
        # Current edit mode for highlighting
        self.current_mode = 'wall'  # 'start', 'target', or 'wall'
        
    def _create_buttons(self) -> Dict[str, pygame.Rect]:
        """Create UI buttons with better layout"""
        buttons = {}
        
        # Control buttons at bottom
        button_y = self.grid_pixel_size + 20
        button_spacing = 110
        
        buttons['start'] = pygame.Rect(20, button_y, 100, 50)
        buttons['pause'] = pygame.Rect(20 + button_spacing, button_y, 100, 50)
        buttons['reset'] = pygame.Rect(20 + button_spacing * 2, button_y, 100, 50)
        buttons['clear'] = pygame.Rect(20 + button_spacing * 3, button_y, 100, 50)
        
        # Algorithm selection buttons in sidebar
        algo_y_start = 120
        algo_button_height = 45
        algo_spacing = 5
        
        algo_names = list(ALGORITHMS.keys())
        for i, name in enumerate(algo_names):
            buttons[f'algo_{name}'] = pygame.Rect(
                self.grid_pixel_size + 20,
                algo_y_start + i * (algo_button_height + algo_spacing),
                130,
                algo_button_height
            )
        
        # Additional utility buttons
        utility_y = algo_y_start + len(algo_names) * (algo_button_height + algo_spacing) + 30
        buttons['random_walls'] = pygame.Rect(
            self.grid_pixel_size + 20,
            utility_y,
            130,
            40
        )
        buttons['clear_dynamic'] = pygame.Rect(
            self.grid_pixel_size + 20,
            utility_y + 50,
            130,
            40
        )
        
        # Animation speed buttons
        speed_y = utility_y + 110
        buttons['speed_slow'] = pygame.Rect(self.grid_pixel_size + 20, speed_y, 60, 35)
        buttons['speed_medium'] = pygame.Rect(self.grid_pixel_size + 85, speed_y, 65, 35)
        
        # Mode selection buttons (Start, Target, Wall)
        mode_y = 50  # Position near the top of sidebar
        mode_button_height = 35
        mode_spacing = 3
        mode_width = 85
        
        buttons['mode_start'] = pygame.Rect(
            self.grid_pixel_size + 15,
            mode_y,
            mode_width,
            mode_button_height
        )
        buttons['mode_target'] = pygame.Rect(
            self.grid_pixel_size + 15,
            mode_y + mode_button_height + mode_spacing,
            mode_width,
            mode_button_height
        )
        buttons['mode_wall'] = pygame.Rect(
            self.grid_pixel_size + 15,
            mode_y + 2 * (mode_button_height + mode_spacing),
            mode_width,
            mode_button_height
        )
        
        return buttons
        
    def draw_grid(self):
        """Draw the search grid with enhanced visuals"""
        for row in range(self.grid.size):
            for col in range(self.grid.size):
                x = col * CELL_SIZE
                y = row * CELL_SIZE
                
                # Get cell color
                cell_state = self.grid.get_cell_state(row, col)
                color = COLORS.get(cell_state, (200, 200, 200))
                
                # Draw cell with rounded corners for modern look
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, color, rect, border_radius=2)
                
                # Draw cell border (subtle)
                border_color = (200, 200, 200) if cell_state == CellState.EMPTY else (150, 150, 150)
                pygame.draw.rect(self.screen, border_color, rect, 1, border_radius=2)
                
                # Draw special markers with better styling
                if cell_state == CellState.START:
                    self._draw_marker('S', x, y, (255, 255, 255), COLORS[CellState.START])
                elif cell_state == CellState.TARGET:
                    self._draw_marker('T', x, y, (255, 255, 255), COLORS[CellState.TARGET])
                elif cell_state == CellState.PATH:
                    # Add glow effect to path
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                     (x + CELL_SIZE//2, y + CELL_SIZE//2), 4)
                    
    def _draw_marker(self, text: str, x: int, y: int, text_color: Tuple[int, int, int], 
                     bg_color: Tuple[int, int, int]):
        """Draw a circular marker for start/target"""
        center = (x + CELL_SIZE//2, y + CELL_SIZE//2)
        radius = CELL_SIZE//2 - 4
        
        # Draw circle background
        pygame.draw.circle(self.screen, bg_color, center, radius)
        # Draw border
        pygame.draw.circle(self.screen, (255, 255, 255), center, radius, 2)
        # Draw text
        self._draw_text(text, center[0], center[1], self.font_medium, text_color, center=True)
        
    def draw_sidebar(self, algorithm_name: str, stats: Dict[str, Any]):
        """Draw sidebar with controls and statistics - Enhanced"""
        sidebar_x = self.grid_pixel_size
        
        # Sidebar background with gradient effect
        sidebar_rect = pygame.Rect(
            sidebar_x, 0, 
            self.sidebar_width, 
            self.grid_pixel_size + self.control_height
        )
        pygame.draw.rect(self.screen, UI_SIDEBAR_COLOR, sidebar_rect)
        
        # Draw border
        pygame.draw.line(self.screen, UI_BORDER_COLOR, 
                        (sidebar_x, 0), 
                        (sidebar_x, self.grid_pixel_size + self.control_height), 2)
        
        # Title with icon effect
        self._draw_text(
            'AI Pathfinder',
            sidebar_x + self.sidebar_width // 2,
            35,
            self.font_title,
            UI_HIGHLIGHT_COLOR,
            center=True
        )
        
        # Subtitle
        self._draw_text(
            'Search Algorithm Visualizer',
            sidebar_x + self.sidebar_width // 2,
            65,
            self.font_small,
            (149, 165, 166),
            center=True
        )

        # Draw mode selection buttons
        mode_configs = {
            'mode_start': ('Start', (46, 204, 113)),  # Green
            'mode_target': ('Target', (231, 76, 60)),  # Red
            'mode_wall': ('Wall', (52, 152, 219))   # Blue
        }

        for mode_key, (label, color) in mode_configs.items():
            if mode_key in self.buttons:
                rect = self.buttons[mode_key]

                # Highlight selected mode with white border
                if self.current_mode == mode_key.replace('mode_', ''):
                    border_color = (255, 255, 255)
                    border_width = 3
                    bg_color = color
                else:
                    border_color = UI_BORDER_COLOR
                    border_width = 1
                    bg_color = (80, 80, 80)  # Darker when not selected

                # Draw button
                pygame.draw.rect(self.screen, bg_color, rect, border_radius=5)
                pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=5)

                # Draw label
                self._draw_text(label, rect.centerx, rect.centery,
                               self.font_small, UI_TEXT_COLOR, center=True)

        # Algorithm selection label
        self._draw_text(
            'Select Algorithm:',
            sidebar_x + 20,
            100,
            self.font_medium,
            UI_TEXT_COLOR
        )
        
        # Draw algorithm buttons with better styling
        for algo_key, algo_name_full in ALGORITHMS.items():
            button_key = f'algo_{algo_key}'
            if button_key in self.buttons:
                rect = self.buttons[button_key]
                
                # Highlight selected algorithm
                if algorithm_name == algo_key:
                    color = UI_BUTTON_ACTIVE
                    border_color = (255, 255, 255)
                    border_width = 2
                else:
                    color = UI_BUTTON_COLOR
                    border_color = UI_BORDER_COLOR
                    border_width = 1
                    
                # Draw button with rounded corners
                pygame.draw.rect(self.screen, color, rect, border_radius=5)
                pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=5)
                
                # Draw algorithm name
                self._draw_text(algo_key, rect.centerx, rect.centery, 
                              self.font_medium, UI_TEXT_COLOR, center=True)
        
        # Draw utility buttons
        rect = self.buttons['random_walls']
        pygame.draw.rect(self.screen, (155, 89, 182), rect, border_radius=5)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, rect, 1, border_radius=5)
        self._draw_text('Random Walls', rect.centerx, rect.centery,
                       self.font_small, UI_TEXT_COLOR, center=True)
        
        rect = self.buttons['clear_dynamic']
        pygame.draw.rect(self.screen, (231, 76, 60), rect, border_radius=5)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, rect, 1, border_radius=5)
        self._draw_text('Clear Dynamic', rect.centerx, rect.centery,
                       self.font_small, UI_TEXT_COLOR, center=True)
        
        # Speed controls
        self._draw_text('Speed:', sidebar_x + 20, self.buttons['speed_slow'].top - 25,
                       self.font_small, UI_TEXT_COLOR)
        
        pygame.draw.rect(self.screen, UI_BUTTON_COLOR, self.buttons['speed_slow'], border_radius=3)
        self._draw_text('Slow', self.buttons['speed_slow'].centerx, 
                       self.buttons['speed_slow'].centery,
                       self.font_small, UI_TEXT_COLOR, center=True)
        
        pygame.draw.rect(self.screen, UI_BUTTON_COLOR, self.buttons['speed_medium'], border_radius=3)
        self._draw_text('Fast', self.buttons['speed_medium'].centerx,
                       self.buttons['speed_medium'].centery,
                       self.font_small, UI_TEXT_COLOR, center=True)
        
        # Statistics panel
        stats_y = 520
        stats_height = 160
        
        # Draw stats panel background
        stats_rect = pygame.Rect(sidebar_x + 10, stats_y, self.sidebar_width - 20, stats_height)
        pygame.draw.rect(self.screen, UI_PANEL_COLOR, stats_rect, border_radius=8)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, stats_rect, 1, border_radius=8)
        
        # Stats title
        self._draw_text('Statistics:', sidebar_x + 20, stats_y + 10,
                       self.font_medium, UI_HIGHLIGHT_COLOR)
        
        # Stats items with color coding
        line_height = 22
        for i, (key, value) in enumerate(stats.items()):
            y_pos = stats_y + 35 + i * line_height
            
            # Status color coding
            if key == 'Status' and value in STATUS_COLORS:
                value_color = STATUS_COLORS[value]
            else:
                value_color = UI_TEXT_COLOR
            
            # Key label
            self._draw_text(f'{key}:', sidebar_x + 20, y_pos,
                          self.font_small, (149, 165, 166))
            
            # Value
            self._draw_text(str(value), sidebar_x + 120, y_pos,
                          self.font_small, value_color)
                          
    def draw_controls(self, is_running: bool, is_paused: bool = False):
        """Draw control buttons - Enhanced"""
        # Control bar background
        control_rect = pygame.Rect(
            0, self.grid_pixel_size, 
            self.grid_pixel_size, self.control_height
        )
        pygame.draw.rect(self.screen, UI_BG_COLOR, control_rect)
        
        # Draw top border
        pygame.draw.line(self.screen, UI_BORDER_COLOR,
                        (0, self.grid_pixel_size),
                        (self.grid_pixel_size, self.grid_pixel_size), 2)
        
        # Draw buttons
        button_configs = {
            'start': ('START', (46, 204, 113) if not is_running else (149, 165, 166)),
            'pause': ('RESUME' if is_paused else 'PAUSE', (241, 196, 15)),
            'reset': ('RESET', (231, 76, 60)),
            'clear': ('CLEAR ALL', (52, 152, 219))
        }
        
        for key, (label, color) in button_configs.items():
            if key in self.buttons:
                rect = self.buttons[key]
                
                # Adjust color for disabled state
                if key == 'start' and is_running:
                    color = (149, 165, 166)
                
                # Draw button
                pygame.draw.rect(self.screen, color, rect, border_radius=8)
                pygame.draw.rect(self.screen, UI_BORDER_COLOR, rect, 1, border_radius=8)
                
                # Draw text
                self._draw_text(label, rect.centerx, rect.centery,
                              self.font_medium, (255, 255, 255), center=True)
                              
    def _draw_text(self, text: str, x: int, y: int, font, color, center=False):
        """Helper to draw text on screen with shadow effect"""
        try:
            # Draw shadow
            shadow_surface = font.render(text, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect()
            if center:
                shadow_rect.center = (x + 1, y + 1)
            else:
                shadow_rect.topleft = (x + 1, y + 1)
            self.screen.blit(shadow_surface, shadow_rect)
            
            # Draw text
            surface = font.render(text, True, color)
            rect = surface.get_rect()
            if center:
                rect.center = (x, y)
            else:
                rect.topleft = (x, y)
            self.screen.blit(surface, rect)
        except Exception as e:
            # Fallback if font rendering fails
            print(f"Text rendering error: {e}")
            
    def draw_message(self):
        """Draw message overlay if active"""
        if self.message and self.message_timer > 0:
            # Calculate opacity based on remaining time
            alpha = min(255, int((self.message_timer / self.message_duration) * 255))
            
            # Create message box
            msg_surface = self.font_medium.render(self.message, True, (255, 255, 255))
            msg_rect = msg_surface.get_rect()
            msg_rect.center = (self.grid_pixel_size // 2, self.grid_pixel_size // 2)
            
            # Draw background
            bg_rect = msg_rect.inflate(20, 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.fill((0, 0, 0))
            bg_surface.set_alpha(alpha * 0.8)
            self.screen.blit(bg_surface, bg_rect)
            
            # Draw text
            self.screen.blit(msg_surface, msg_rect)
            
            # Decrease timer
            self.message_timer -= self.clock.get_time()
            if self.message_timer <= 0:
                self.message = ""
                
    def show_message(self, text: str, duration: int = 3000):
        """Show a message overlay"""
        self.message = text
        self.message_timer = duration
        
    def render(self, algorithm_name: str = "", stats: Dict[str, Any] = None, 
               is_running: bool = False, is_paused: bool = False):
        """Main render function"""
        if stats is None:
            stats = {}
            
        self.screen.fill(UI_BG_COLOR)
        self.draw_grid()
        self.draw_sidebar(algorithm_name, stats)
        self.draw_controls(is_running, is_paused)
        self.draw_message()
        
        pygame.display.flip()
        self.clock.tick(FPS)
        
    def get_cell_from_mouse(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convert mouse position to grid cell coordinates"""
        x, y = pos
        if x < self.grid_pixel_size and y < self.grid_pixel_size:
            col = x // CELL_SIZE
            row = y // CELL_SIZE
            if 0 <= row < self.grid.size and 0 <= col < self.grid.size:
                return (row, col)
        return None
        
    def get_clicked_button(self, pos: Tuple[int, int]) -> Optional[str]:
        """Check if a button was clicked"""
        for name, rect in self.buttons.items():
            if rect.collidepoint(pos):
                return name
        return None
        
    def animate_step(self, visited_nodes: List[Tuple[int, int]], 
                    frontier_nodes: List[List[Tuple[int, int]]],
                    step_index: int):
        """Animate a single step of the search"""
        if step_index < len(visited_nodes):
            node = visited_nodes[step_index]
            self.grid.mark_explored(node[0], node[1])
            
        # Mark frontier nodes
        if step_index < len(frontier_nodes):
            for node in frontier_nodes[step_index]:
                if self.grid.get_cell_state(node[0], node[1]) == CellState.EMPTY:
                    self.grid.mark_frontier(node[0], node[1])
                    
        pygame.time.delay(self.animation_delay)
        
    def show_path(self, path: List[Tuple[int, int]]):
        """Highlight the final path"""
        self.grid.mark_path(path)
        
    def update_display(self):
        """Update the display"""
        pygame.display.flip()
        
    def handle_events(self) -> List[Tuple[str, Any]]:
        """Handle pygame events, return list of actions"""
        actions = []
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                actions.append(('quit', None))
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    button = self.get_clicked_button(event.pos)
                    if button:
                        actions.append(('button_click', button))
                    else:
                        cell = self.get_cell_from_mouse(event.pos)
                        if cell:
                            actions.append(('cell_click', cell))
                            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    actions.append(('key_press', 'space'))
                elif event.key == pygame.K_r:
                    actions.append(('key_press', 'r'))
                elif event.key == pygame.K_c:
                    actions.append(('key_press', 'c'))
                elif event.key == pygame.K_p:
                    actions.append(('key_press', 'p'))
                elif event.key == pygame.K_s:
                    actions.append(('key_press', 's'))
                    
        return actions
        
    def quit(self):
        """Clean up pygame"""
        pygame.quit()

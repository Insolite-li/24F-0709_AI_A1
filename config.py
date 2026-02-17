"""
Configuration and Constants for AI Pathfinder - ENHANCED VERSION
"""
import pygame

# Window Configuration
WINDOW_TITLE = "FOUND YOU....."
GRID_SIZE = 30
CELL_SIZE = 25
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE + 320  # Extra space for sidebar
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE + 120  # Extra space for controls
FPS = 60

# Animation Settings
ANIMATION_DELAY = 50  # milliseconds between steps (50ms = fast, 100ms = medium, 200ms = slow)
ENABLE_ANIMATION = True

# Dynamic Obstacle Settings
DYNAMIC_OBSTACLE_PROBABILITY = 0.03  # 3% chance per step
MAX_DYNAMIC_OBSTACLES = 50

# Grid Cell States
class CellState:
    EMPTY = 0
    WALL = -1
    START = 1
    TARGET = 2
    FRONTIER = 3
    EXPLORED = 4
    PATH = 5
    DYNAMIC_OBSTACLE = 6

# Colors (RGB) - Enhanced color palette
COLORS = {
    CellState.EMPTY: (255, 255, 255),           # White
    CellState.WALL: (45, 52, 54),               # Dark Gray
    CellState.START: (46, 204, 113),            # Green ( brighter)
    CellState.TARGET: (231, 76, 60),            # Red (brighter)
    CellState.FRONTIER: (52, 152, 219),         # Blue
    CellState.EXPLORED: (241, 196, 15),         # Yellow
    CellState.PATH: (155, 89, 182),             # Purple
    CellState.DYNAMIC_OBSTACLE: (127, 140, 141), # Gray
}

# Movement Directions (Clockwise: Up, Right, Bottom, Bottom-Right, Left, Top-Left)
# Note: Top-Right and Bottom-Left are intentionally EXCLUDED
DIRECTIONS = [
    (-1, 0),    # Up
    (0, 1),     # Right
    (1, 0),     # Bottom
    (1, 1),     # Bottom-Right (Diagonal)
    (0, -1),    # Left
    (-1, -1),   # Top-Left (Diagonal)
]

DIRECTION_NAMES = ["Up", "Right", "Bottom", "Bottom-Right", "Left", "Top-Left"]

# Algorithm Names
ALGORITHMS = {
    "BFS": "Breadth-First Search",
    "DFS": "Depth-First Search", 
    "UCS": "Uniform-Cost Search",
    "DLS": "Depth-Limited Search",
    "IDDFS": "Iterative Deepening DFS",
    "Bidir": "Bidirectional Search"
}

# UI Colors - Enhanced modern dark theme
UI_BG_COLOR = (30, 30, 35)
UI_TEXT_COLOR = (236, 240, 241)
UI_BUTTON_COLOR = (52, 73, 94)
UI_BUTTON_HOVER = (67, 90, 112)
UI_BUTTON_ACTIVE = (46, 204, 113)
UI_SIDEBAR_COLOR = (25, 25, 30)
UI_PANEL_COLOR = (40, 44, 52)
UI_BORDER_COLOR = (64, 68, 75)
UI_HIGHLIGHT_COLOR = (52, 152, 219)

# Status Colors
STATUS_COLORS = {
    'Idle': (149, 165, 166),
    'Running': (52, 152, 219),
    'Path Found': (46, 204, 113),
    'No Path': (231, 76, 60),
    'Replanning': (241, 196, 15),
    'Blocked': (231, 76, 60),
    'Reset': (149, 165, 166),
    'Cleared': (149, 165, 166),
}

# Fonts
FONT_SIZE_SMALL = 14
FONT_SIZE_MEDIUM = 18
FONT_SIZE_LARGE = 22
FONT_SIZE_TITLE = 28

# Animation Settings
ANIMATION_SPEEDS = {
    'Slow': 200,
    'Medium': 100,
    'Fast': 50,
    'Instant': 0
}

# Grid Presets
GRID_PRESETS = {
    'Small': 20,
    'Medium': 30,
    'Large': 40,
    'Extra Large': 50
}

# Error Messages
ERROR_MESSAGES = {
    'INVALID_POSITION': 'Invalid position specified',
    'OUT_OF_BOUNDS': 'Position out of grid bounds',
    'START_TARGET_SAME': 'Start and target cannot be the same',
    'NO_PATH': 'No valid path found',
    'ALGORITHM_ERROR': 'Algorithm execution error',
}

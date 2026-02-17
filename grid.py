"""
Grid Module - Manages the grid state and cell information - ENHANCED WITH ERROR HANDLING
"""
from typing import List, Tuple, Optional, Set
import random
import logging
from config import CellState, DIRECTIONS, GRID_SIZE, DYNAMIC_OBSTACLE_PROBABILITY, MAX_DYNAMIC_OBSTACLES, ERROR_MESSAGES

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Grid:
    """
    Represents the search grid environment.
    Handles cell states, obstacles, and position tracking.
    """
    
    def __init__(self, size: int = GRID_SIZE):
        if not isinstance(size, int) or size <= 0:
            raise ValueError(f"Grid size must be a positive integer, got {size}")
        
        self.size = size
        self.grid: List[List[int]] = [[CellState.EMPTY for _ in range(size)] for _ in range(size)]
        self.start_pos: Optional[Tuple[int, int]] = None
        self.target_pos: Optional[Tuple[int, int]] = None
        self.dynamic_obstacles: Set[Tuple[int, int]] = set()
        self.static_walls: Set[Tuple[int, int]] = set()
        
    def initialize_default(self):
        """Initialize with default start and target positions"""
        self.start_pos = (1, 1)
        self.target_pos = (self.size - 2, self.size - 2)
        self.grid[self.start_pos[0]][self.start_pos[1]] = CellState.START
        self.grid[self.target_pos[0]][self.target_pos[1]] = CellState.TARGET
        
    def _validate_position(self, row: int, col: int) -> bool:
        """Validate if position is within bounds"""
        return 0 <= row < self.size and 0 <= col < self.size
        
    def set_start(self, row: int, col: int) -> bool:
        """Set the start position with validation"""
        if not self._validate_position(row, col):
            logger.error(f"Cannot set start: {ERROR_MESSAGES['OUT_OF_BOUNDS']} ({row}, {col})")
            return False
            
        if (row, col) == self.target_pos:
            logger.warning("Cannot set start: Start and target cannot be the same")
            return False
            
        if self.start_pos:
            old_row, old_col = self.start_pos
            self.grid[old_row][old_col] = CellState.EMPTY
        self.start_pos = (row, col)
        self.grid[row][col] = CellState.START
        return True
        
    def set_target(self, row: int, col: int) -> bool:
        """Set the target position with validation"""
        if not self._validate_position(row, col):
            logger.error(f"Cannot set target: {ERROR_MESSAGES['OUT_OF_BOUNDS']} ({row}, {col})")
            return False
            
        if (row, col) == self.start_pos:
            logger.warning("Cannot set target: Start and target cannot be the same")
            return False
            
        if self.target_pos:
            old_row, old_col = self.target_pos
            self.grid[old_row][old_col] = CellState.EMPTY
        self.target_pos = (row, col)
        self.grid[row][col] = CellState.TARGET
        return True
        
    def add_wall(self, row: int, col: int) -> bool:
        """Add a static wall with validation"""
        if not self._validate_position(row, col):
            return False
            
        if (row, col) == self.start_pos or (row, col) == self.target_pos:
            logger.warning(f"Cannot add wall at ({row}, {col}): Position is start or target")
            return False
            
        self.grid[row][col] = CellState.WALL
        self.static_walls.add((row, col))
        return True
            
    def remove_wall(self, row: int, col: int) -> bool:
        """Remove a wall with validation"""
        if not self._validate_position(row, col):
            return False
            
        if self.grid[row][col] == CellState.WALL:
            self.grid[row][col] = CellState.EMPTY
            self.static_walls.discard((row, col))
            return True
        return False
            
    def clear_walls(self):
        """Clear all walls"""
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == CellState.WALL:
                    self.grid[row][col] = CellState.EMPTY
        self.static_walls.clear()
        
    def spawn_dynamic_obstacle(self) -> Optional[Tuple[int, int]]:
        """
        Spawn a dynamic obstacle with given probability.
        Returns the position if spawned, None otherwise.
        """
        if len(self.dynamic_obstacles) >= MAX_DYNAMIC_OBSTACLES:
            return None
            
        if random.random() < DYNAMIC_OBSTACLE_PROBABILITY:
            # Find empty cells
            empty_cells = []
            for row in range(self.size):
                for col in range(self.size):
                    if (self.grid[row][col] == CellState.EMPTY and 
                        (row, col) != self.start_pos and 
                        (row, col) != self.target_pos):
                        empty_cells.append((row, col))
            
            if empty_cells:
                pos = random.choice(empty_cells)
                self.grid[pos[0]][pos[1]] = CellState.DYNAMIC_OBSTACLE
                self.dynamic_obstacles.add(pos)
                return pos
        return None
        
    def remove_dynamic_obstacle(self, row: int, col: int) -> bool:
        """Remove a dynamic obstacle with validation"""
        if not self._validate_position(row, col):
            return False
            
        if (row, col) in self.dynamic_obstacles:
            self.grid[row][col] = CellState.EMPTY
            self.dynamic_obstacles.remove((row, col))
            return True
        return False
        
    def clear_dynamic_obstacles(self):
        """Clear all dynamic obstacles"""
        for row, col in list(self.dynamic_obstacles):
            self.grid[row][col] = CellState.EMPTY
        self.dynamic_obstacles.clear()
        
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within grid bounds"""
        return self._validate_position(row, col)
        
    def is_walkable(self, row: int, col: int) -> bool:
        """Check if position is walkable (not a wall or obstacle)"""
        if not self._validate_position(row, col):
            return False
        return self.grid[row][col] not in [CellState.WALL, CellState.DYNAMIC_OBSTACLE]
        
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Get valid neighbors in clockwise order:
        Up, Right, Bottom, Bottom-Right, Left, Top-Left
        """
        if not self._validate_position(row, col):
            return []
            
        neighbors = []
        for dr, dc in DIRECTIONS:
            new_row, new_col = row + dr, col + dc
            if self.is_walkable(new_row, new_col):
                neighbors.append((new_row, new_col))
        return neighbors
        
    def mark_frontier(self, row: int, col: int) -> bool:
        """Mark a cell as frontier (to be explored)"""
        if not self._validate_position(row, col):
            return False
            
        if self.grid[row][col] == CellState.EMPTY:
            self.grid[row][col] = CellState.FRONTIER
            return True
        return False
            
    def mark_explored(self, row: int, col: int) -> bool:
        """Mark a cell as explored"""
        if not self._validate_position(row, col):
            return False
            
        if self.grid[row][col] in [CellState.FRONTIER, CellState.EMPTY]:
            self.grid[row][col] = CellState.EXPLORED
            return True
        return False
            
    def mark_path(self, path: List[Tuple[int, int]]) -> int:
        """Mark the final path, returns number of cells marked"""
        marked = 0
        for row, col in path:
            if self._validate_position(row, col):
                if (row, col) != self.start_pos and (row, col) != self.target_pos:
                    if self.grid[row][col] not in [CellState.WALL, CellState.DYNAMIC_OBSTACLE]:
                        self.grid[row][col] = CellState.PATH
                        marked += 1
        return marked
                
    def clear_search_visualization(self):
        """Clear frontier, explored, and path marks"""
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] in [CellState.FRONTIER, CellState.EXPLORED, CellState.PATH]:
                    self.grid[row][col] = CellState.EMPTY
                    
    def reset(self):
        """Reset grid to initial state (keep walls and start/target)"""
        self.clear_search_visualization()
        self.clear_dynamic_obstacles()
        
    def is_path_blocked(self, path: List[Tuple[int, int]]) -> bool:
        """Check if any cell in the path is now blocked"""
        if not path:
            return False
            
        for row, col in path:
            if not self.is_walkable(row, col):
                return True
        return False
        
    def get_cell_state(self, row: int, col: int) -> int:
        """Get the state of a cell"""
        if not self._validate_position(row, col):
            return CellState.WALL  # Return wall for out of bounds
        return self.grid[row][col]
        
    def randomize_walls(self, density: float = 0.3):
        """Randomly place walls with given density (0.0 to 1.0)"""
        if not (0 <= density <= 1):
            logger.error(f"Invalid density: {density}. Must be between 0 and 1")
            return
            
        self.clear_walls()
        walls_added = 0
        for row in range(self.size):
            for col in range(self.size):
                if (row, col) != self.start_pos and (row, col) != self.target_pos:
                    if random.random() < density:
                        if self.add_wall(row, col):
                            walls_added += 1
                            
        logger.info(f"Randomized {walls_added} walls with density {density}")

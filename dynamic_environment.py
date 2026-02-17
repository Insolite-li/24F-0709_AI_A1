"""
Dynamic Environment Module
Handles dynamic obstacle spawning and re-planning logic
"""
from typing import Tuple, Optional, List
import random
from grid import Grid
from algorithms.base_search import SearchResult, SearchStatus
from config import DYNAMIC_OBSTACLE_PROBABILITY, CellState

class DynamicEnvironment:
    """
    Manages dynamic obstacles and handles re-planning.
    """
    
    def __init__(self, grid: Grid):
        self.grid = grid
        self.replan_count = 0
        self.blocked_paths = 0
        
    def spawn_dynamic_obstacle(self) -> Optional[Tuple[int, int]]:
        """
        Spawn a dynamic obstacle with probability check.
        Returns position if spawned, None otherwise.
        """
        return self.grid.spawn_dynamic_obstacle()
        
    def check_path_blocked(self, path: List[Tuple[int, int]], current_index: int) -> bool:
        """
        Check if the remaining path is blocked by dynamic obstacles.
        current_index is the agent's current position in the path.
        """
        if not path or current_index >= len(path):
            return False
            
        # Check remaining path
        for i in range(current_index, len(path)):
            row, col = path[i]
            if not self.grid.is_walkable(row, col):
                self.blocked_paths += 1
                return True
        return False
        
    def replan_needed(self, result: SearchResult, current_pos: Tuple[int, int]) -> bool:
        """
        Determine if re-planning is needed based on:
        1. Current path is blocked
        2. Next intended node is blocked
        """
        if result.status != SearchStatus.FOUND or not result.path:
            return False
            
        # Find current position in path
        try:
            current_index = result.path.index(current_pos)
        except ValueError:
            # Current position not in path, definitely need replan
            return True
            
        # Check if remaining path is blocked
        if self.check_path_blocked(result.path, current_index + 1):
            return True
            
        # Check next intended node
        next_index = current_index + 1
        if next_index < len(result.path):
            next_row, next_col = result.path[next_index]
            if not self.grid.is_walkable(next_row, next_col):
                return True
                
        return False
        
    def trigger_replan(self, current_pos: Tuple[int, int], 
                       algorithm, get_neighbors_func) -> SearchResult:
        """
        Trigger re-planning from current position.
        Returns new search result.
        """
        self.replan_count += 1
        
        # Clear previous search visualization
        self.grid.clear_search_visualization()
        
        # Run search from current position
        result = algorithm.search(
            start=current_pos,
            target=self.grid.target_pos,
            get_neighbors_func=get_neighbors_func
        )
        
        return result
        
    def get_stats(self) -> dict:
        """Get dynamic environment statistics"""
        return {
            'replan_count': self.replan_count,
            'blocked_paths': self.blocked_paths,
            'dynamic_obstacles': len(self.grid.dynamic_obstacles)
        }
        
    def reset(self):
        """Reset environment statistics"""
        self.replan_count = 0
        self.blocked_paths = 0

"""
Base Search Algorithm Module
Provides abstract base class for all search algorithms
"""
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass
from enum import Enum

class SearchStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    FOUND = "found"
    NOT_FOUND = "not_found"
    BLOCKED = "blocked"

@dataclass
class SearchResult:
    """Result of a search algorithm"""
    path: Optional[List[Tuple[int, int]]]
    visited_nodes: List[Tuple[int, int]]
    frontier_nodes: List[List[Tuple[int, int]]]
    steps: int
    status: SearchStatus
    message: str
    
class BaseSearch(ABC):
    """
    Abstract base class for all search algorithms.
    Provides common interface and utility methods.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.full_name = ""
        self.status = SearchStatus.IDLE
        self.visited: Set[Tuple[int, int]] = set()
        self.frontier: List[Tuple[int, int]] = []
        self.parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}
        self.steps = 0
        self.current_pos: Optional[Tuple[int, int]] = None
        
    @abstractmethod
    def search(self, start: Tuple[int, int], target: Tuple[int, int], 
               get_neighbors_func) -> SearchResult:
        """
        Execute the search algorithm.
        
        Args:
            start: Starting position (row, col)
            target: Target position (row, col)
            get_neighbors_func: Function that returns valid neighbors
            
        Returns:
            SearchResult with path and statistics
        """
        pass
        
    def reconstruct_path(self, target: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from target to start using parent pointers"""
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = self.parent.get(current)
        return path[::-1]  # Reverse to get start -> target
        
    def reset(self):
        """Reset algorithm state"""
        self.status = SearchStatus.IDLE
        self.visited.clear()
        self.frontier.clear()
        self.parent.clear()
        self.steps = 0
        self.current_pos = None

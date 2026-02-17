"""
Bidirectional Search Algorithm - FIXED VERSION
Searches simultaneously from start and target, meeting in the middle
Much faster than unidirectional search in most cases
"""
from typing import Tuple, List, Set, Dict, Optional
from collections import deque
from algorithms.base_search import BaseSearch, SearchResult, SearchStatus

class BidirectionalSearch(BaseSearch):
    """Bidirectional Search implementation - FIXED"""
    
    def __init__(self):
        super().__init__("BIDIRECTIONAL")
        self.full_name = "Bidirectional Search"
        self.frontier_start: Set[Tuple[int, int]] = set()
        self.frontier_target: Set[Tuple[int, int]] = set()
        self.parent_start: Dict[Tuple[int, int], Tuple[int, int]] = {}
        self.parent_target: Dict[Tuple[int, int], Tuple[int, int]] = {}
        
    def reset(self):
        super().reset()
        self.frontier_start.clear()
        self.frontier_target.clear()
        self.parent_start.clear()
        self.parent_target.clear()
        
    def search(self, start: Tuple[int, int], target: Tuple[int, int], 
               get_neighbors_func) -> SearchResult:
        """
        Bidirectional search runs two simultaneous searches:
        - Forward from start
        - Backward from target
        They meet in the middle, significantly reducing the search space.
        """
        self.reset()
        self.status = SearchStatus.RUNNING
        
        # Handle start == target
        if start == target:
            self.status = SearchStatus.FOUND
            return SearchResult(
                path=[start],
                visited_nodes=[start],
                frontier_nodes=[[]],
                steps=1,
                status=self.status,
                message="Start is target!"
            )
        
        # Initialize frontiers (BFS from both sides)
        queue_start = deque([start])
        queue_target = deque([target])
        
        self.frontier_start.add(start)
        self.frontier_target.add(target)
        
        self.parent_start[start] = start  # Self-reference for root
        self.parent_target[target] = target  # Self-reference for root
        
        visited_start: Set[Tuple[int, int]] = {start}
        visited_target: Set[Tuple[int, int]] = {target}
        
        visited_order = []
        frontier_history = []
        
        meeting_point: Optional[Tuple[int, int]] = None
        
        while queue_start and queue_target:
            self.steps += 1
            
            # Expand from start side
            current_start = queue_start.popleft()
            self.frontier_start.discard(current_start)
            self.current_pos = current_start
            visited_order.append(current_start)
            
            for neighbor in get_neighbors_func(current_start[0], current_start[1]):
                if neighbor not in visited_start:
                    visited_start.add(neighbor)
                    self.parent_start[neighbor] = current_start
                    queue_start.append(neighbor)
                    self.frontier_start.add(neighbor)
                    
                    # Check if we met the other search
                    if neighbor in visited_target:
                        meeting_point = neighbor
                        break
            
            if meeting_point:
                break
            
            # Expand from target side
            if queue_target:
                current_target = queue_target.popleft()
                self.frontier_target.discard(current_target)
                self.current_pos = current_target
                visited_order.append(current_target)
                
                for neighbor in get_neighbors_func(current_target[0], current_target[1]):
                    if neighbor not in visited_target:
                        visited_target.add(neighbor)
                        self.parent_target[neighbor] = current_target
                        queue_target.append(neighbor)
                        self.frontier_target.add(neighbor)
                        
                        # Check if we met the other search
                        if neighbor in visited_start:
                            meeting_point = neighbor
                            break
            
            # Record frontiers for visualization
            combined_frontier = list(self.frontier_start | self.frontier_target)
            frontier_history.append(combined_frontier)
            
            if meeting_point:
                break
        
        if meeting_point:
            # Reconstruct path from both sides
            path = self._reconstruct_bidirectional_path(meeting_point)
            self.status = SearchStatus.FOUND
            return SearchResult(
                path=path,
                visited_nodes=visited_order,
                frontier_nodes=frontier_history,
                steps=self.steps,
                status=self.status,
                message=f"Path found! Length: {len(path)}, Visited: {len(visited_order)} (Bidirectional)"
            )
        
        self.status = SearchStatus.NOT_FOUND
        return SearchResult(
            path=None,
            visited_nodes=visited_order,
            frontier_nodes=frontier_history,
            steps=self.steps,
            status=self.status,
            message=f"No path found. Visited: {len(visited_order)} nodes"
        )
    
    def _reconstruct_bidirectional_path(self, meeting_point: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from start to target through meeting point"""
        # Path from start to meeting point
        path_start = []
        current = meeting_point
        max_iterations = 1000  # Safety limit
        iterations = 0
        
        while current != self.parent_start.get(current, current) and iterations < max_iterations:
            path_start.append(current)
            parent = self.parent_start.get(current)
            if parent is None or parent == current:
                break
            current = parent
            iterations += 1
        
        # Add start node if not already added
        if current != meeting_point:
            path_start.append(current)
        
        path_start = path_start[::-1]  # Reverse to get start -> meeting_point
        
        # Path from meeting point to target
        path_target = []
        current = self.parent_target.get(meeting_point)
        iterations = 0
        
        if current is not None:
            while current != self.parent_target.get(current, current) and iterations < max_iterations:
                path_target.append(current)
                parent = self.parent_target.get(current)
                if parent is None or parent == current:
                    break
                current = parent
                iterations += 1
            
            # Add target node
            if current is not None:
                path_target.append(current)
        
        # Combine paths
        return path_start + path_target

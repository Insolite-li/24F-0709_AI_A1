"""
Depth-Limited Search (DLS) Algorithm - FIXED VERSION
DFS with a maximum depth limit to prevent infinite loops
"""
from typing import Tuple, List, Set, Optional
from algorithms.base_search import BaseSearch, SearchResult, SearchStatus

class DLS(BaseSearch):
    """Depth-Limited Search implementation - FIXED"""
    
    def __init__(self, depth_limit: int = 20):
        super().__init__("DLS")
        self.full_name = "Depth-Limited Search"
        self.depth_limit = depth_limit
        
    def reset(self):
        super().reset()
        
    def search(self, start: Tuple[int, int], target: Tuple[int, int], 
               get_neighbors_func) -> SearchResult:
        """
        DLS performs DFS up to a specified depth limit.
        Prevents infinite loops in deep/infinite graphs.
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
        
        visited: Set[Tuple[int, int]] = set()
        parent: dict = {start: start}  # Use self-reference instead of None
        visited_order = []
        frontier_history = []
        found_path: Optional[List[Tuple[int, int]]] = None
        
        def dls_recursive(node: Tuple[int, int], depth: int) -> bool:
            """Recursive DLS helper - returns True if target found"""
            nonlocal found_path
            self.steps += 1
            self.current_pos = node
            
            if node not in visited:
                visited.add(node)
                visited_order.append(node)
            
            # Record frontier (stack-like)
            frontier_history.append([])
            
            if node == target:
                found_path = self._reconstruct_path(parent, target)
                return True
            
            if depth >= self.depth_limit:
                return False
            
            # Get neighbors
            neighbors = get_neighbors_func(node[0], node[1])
            
            for neighbor in neighbors:
                if neighbor not in visited and neighbor not in parent:
                    parent[neighbor] = node
                    if dls_recursive(neighbor, depth + 1):
                        return True
            
            return False
        
        # Run search
        found = dls_recursive(start, 0)
        
        if found and found_path:
            self.status = SearchStatus.FOUND
            return SearchResult(
                path=found_path,
                visited_nodes=visited_order,
                frontier_nodes=frontier_history,
                steps=self.steps,
                status=self.status,
                message=f"Path found within depth {self.depth_limit}! Length: {len(found_path)}, Visited: {len(visited_order)}"
            )
        else:
            self.status = SearchStatus.NOT_FOUND
            return SearchResult(
                path=None,
                visited_nodes=visited_order,
                frontier_nodes=frontier_history,
                steps=self.steps,
                status=self.status,
                message=f"No path found within depth {self.depth_limit}. Visited: {len(visited_order)} nodes"
            )
    
    def _reconstruct_path(self, parent: dict, target: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from parent pointers"""
        path = []
        current = target
        start = target  # Find start
        for node, par in parent.items():
            if par == node:  # Self-reference is start
                start = node
                break
        
        while current != start:
            path.append(current)
            current = parent.get(current, start)
            if current == target:  # Prevent infinite loop
                break
        path.append(start)
        return path[::-1]

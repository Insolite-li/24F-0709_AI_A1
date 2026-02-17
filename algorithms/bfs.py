"""
Breadth-First Search (BFS) Algorithm
Explores all neighbors at current depth before moving deeper
"""
from typing import Tuple, List
from collections import deque
from algorithms.base_search import BaseSearch, SearchResult, SearchStatus

class BFS(BaseSearch):
    """Breadth-First Search implementation"""
    
    def __init__(self):
        super().__init__("BFS")
        self.full_name = "Breadth-First Search"
        
    def search(self, start: Tuple[int, int], target: Tuple[int, int], 
               get_neighbors_func) -> SearchResult:
        """
        BFS explores nodes level by level, guaranteeing shortest path in unweighted grid.
        Uses queue (FIFO) for frontier.
        """
        self.reset()
        self.status = SearchStatus.RUNNING
        
        queue = deque([start])
        self.visited.add(start)
        self.parent[start] = None
        
        visited_order = []
        frontier_history = []
        
        while queue:
            self.steps += 1
            current = queue.popleft()
            self.current_pos = current
            visited_order.append(current)
            
            # Record frontier for visualization
            frontier_history.append(list(queue))
            
            if current == target:
                path = self.reconstruct_path(target)
                self.status = SearchStatus.FOUND
                return SearchResult(
                    path=path,
                    visited_nodes=visited_order,
                    frontier_nodes=frontier_history,
                    steps=self.steps,
                    status=self.status,
                    message=f"Path found! Length: {len(path)}, Visited: {len(visited_order)}"
                )
            
            # Get neighbors in clockwise order
            for neighbor in get_neighbors_func(current[0], current[1]):
                if neighbor not in self.visited:
                    self.visited.add(neighbor)
                    self.parent[neighbor] = current
                    queue.append(neighbor)
                    
        self.status = SearchStatus.NOT_FOUND
        return SearchResult(
            path=None,
            visited_nodes=visited_order,
            frontier_nodes=frontier_history,
            steps=self.steps,
            status=self.status,
            message=f"No path found. Visited: {len(visited_order)} nodes"
        )

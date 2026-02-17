"""
Depth-First Search (DFS) Algorithm
Explores as far as possible along each branch before backtracking
"""
from typing import Tuple, List
from algorithms.base_search import BaseSearch, SearchResult, SearchStatus

class DFS(BaseSearch):
    """Depth-First Search implementation"""
    
    def __init__(self):
        super().__init__("DFS")
        self.full_name = "Depth-First Search"
        
    def search(self, start: Tuple[int, int], target: Tuple[int, int], 
               get_neighbors_func) -> SearchResult:
        """
        DFS explores deep into the graph before backtracking.
        Uses stack (LIFO) for frontier.
        Note: Does not guarantee shortest path.
        """
        self.reset()
        self.status = SearchStatus.RUNNING
        
        stack = [start]
        self.visited.add(start)
        self.parent[start] = None
        
        visited_order = []
        frontier_history = []
        
        while stack:
            self.steps += 1
            current = stack.pop()
            self.current_pos = current
            visited_order.append(current)
            
            # Record frontier for visualization
            frontier_history.append(list(stack))
            
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
            
            # Get neighbors in clockwise order (reversed for correct DFS behavior)
            neighbors = get_neighbors_func(current[0], current[1])
            for neighbor in reversed(neighbors):  # Reverse to maintain clockwise order
                if neighbor not in self.visited:
                    self.visited.add(neighbor)
                    self.parent[neighbor] = current
                    stack.append(neighbor)
                    
        self.status = SearchStatus.NOT_FOUND
        return SearchResult(
            path=None,
            visited_nodes=visited_order,
            frontier_nodes=frontier_history,
            steps=self.steps,
            status=self.status,
            message=f"No path found. Visited: {len(visited_order)} nodes"
        )

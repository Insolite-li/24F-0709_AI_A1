"""
Iterative Deepening DFS (IDDFS) Algorithm - FIXED VERSION
Performs DFS with increasing depth limits until goal is found
Combines benefits of BFS (completeness, optimal) and DFS (space efficiency)
"""
from typing import Tuple, List, Set, Optional, Dict
from algorithms.base_search import BaseSearch, SearchResult, SearchStatus

class IDDFS(BaseSearch):
    """Iterative Deepening DFS implementation - FIXED"""
    
    def __init__(self, max_depth: int = 100):
        super().__init__("IDDFS")
        self.full_name = "Iterative Deepening DFS"
        self.max_depth = max_depth
        
    def reset(self):
        super().reset()
        
    def search(self, start: Tuple[int, int], target: Tuple[int, int], 
               get_neighbors_func) -> SearchResult:
        """
        IDDFS calls DLS with increasing depth limits (0, 1, 2, ...)
        until the target is found or max_depth is reached.
        Combines space efficiency of DFS with completeness of BFS.
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
        
        all_visited_order: List[Tuple[int, int]] = []
        all_frontier_history: List[List[Tuple[int, int]]] = []
        total_steps = 0
        
        for depth_limit in range(self.max_depth + 1):
            # Reset for this iteration
            iteration_visited: Set[Tuple[int, int]] = set()
            parent: Dict[Tuple[int, int], Tuple[int, int]] = {start: start}
            found_path: Optional[List[Tuple[int, int]]] = None
            
            # Use iterative stack instead of recursion to avoid issues
            stack = [(start, 0)]  # (node, depth)
            
            while stack and found_path is None:
                node, depth = stack.pop()
                total_steps += 1
                self.steps = total_steps
                self.current_pos = node
                
                # Add to iteration visited
                if node not in iteration_visited:
                    iteration_visited.add(node)
                    all_visited_order.append(node)
                
                # Record frontier
                frontier_snapshot = [n for n, d in stack]
                all_frontier_history.append(frontier_snapshot)
                
                if node == target:
                    found_path = self._reconstruct_path_from_parent(parent, target)
                    break
                
                if depth >= depth_limit:
                    continue
                
                # Get neighbors in reverse order for correct DFS behavior
                neighbors = get_neighbors_func(node[0], node[1])
                for neighbor in reversed(neighbors):
                    if neighbor not in iteration_visited and neighbor not in parent:
                        parent[neighbor] = node
                        stack.append((neighbor, depth + 1))
            
            # Check if we found the path
            if found_path is not None:
                self.status = SearchStatus.FOUND
                return SearchResult(
                    path=found_path,
                    visited_nodes=all_visited_order,
                    frontier_nodes=all_frontier_history,
                    steps=total_steps,
                    status=self.status,
                    message=f"Path found at depth {depth_limit}! Length: {len(found_path)}, Total Visited: {len(all_visited_order)}"
                )
            
            # If we didn't find it and reached max depth, stop
            if depth_limit >= self.max_depth:
                break
        
        self.status = SearchStatus.NOT_FOUND
        return SearchResult(
            path=None,
            visited_nodes=all_visited_order,
            frontier_nodes=all_frontier_history,
            steps=total_steps,
            status=self.status,
            message=f"No path found within max depth {self.max_depth}. Total Visited: {len(all_visited_order)}"
        )
    
    def _reconstruct_path_from_parent(self, parent: Dict[Tuple[int, int], Tuple[int, int]], 
                                      target: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from parent pointers"""
        path = []
        current = target
        
        # Find start node (self-referencing parent)
        start = target
        for node, par in parent.items():
            if par == node:
                start = node
                break
        
        max_iterations = 1000
        iterations = 0
        while current != start and iterations < max_iterations:
            path.append(current)
            next_node = parent.get(current)
            if next_node is None or next_node == current:
                break
            current = next_node
            iterations += 1
        
        if current is not None:
            path.append(current)
        return path[::-1]

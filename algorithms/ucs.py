"""
Uniform-Cost Search (UCS) Algorithm
Expands the node with lowest path cost first
"""
from typing import Tuple, List
import heapq
from algorithms.base_search import BaseSearch, SearchResult, SearchStatus

class UCS(BaseSearch):
    """Uniform-Cost Search implementation"""
    
    def __init__(self):
        super().__init__("UCS")
        self.full_name = "Uniform-Cost Search"
        self.cost = {}
        
    def reset(self):
        super().reset()
        self.cost = {}
        
    def search(self, start: Tuple[int, int], target: Tuple[int, int], 
               get_neighbors_func) -> SearchResult:
        """
        UCS always expands the node with the lowest cumulative cost.
        Uses priority queue ordered by path cost.
        With uniform edge costs (1), behaves like BFS but tracks costs.
        """
        self.reset()
        self.status = SearchStatus.RUNNING
        
        # Priority queue: (cost, counter, node)
        counter = 0
        priority_queue = [(0, counter, start)]
        self.visited.add(start)
        self.parent[start] = None
        self.cost[start] = 0
        
        visited_order = []
        frontier_history = []
        
        while priority_queue:
            self.steps += 1
            current_cost, _, current = heapq.heappop(priority_queue)
            self.current_pos = current
            visited_order.append(current)
            
            # Record frontier for visualization (without costs)
            frontier_nodes = [node for (_, _, node) in priority_queue]
            frontier_history.append(frontier_nodes)
            
            if current == target:
                path = self.reconstruct_path(target)
                self.status = SearchStatus.FOUND
                return SearchResult(
                    path=path,
                    visited_nodes=visited_order,
                    frontier_nodes=frontier_history,
                    steps=self.steps,
                    status=self.status,
                    message=f"Path found! Length: {len(path)}, Cost: {current_cost}, Visited: {len(visited_order)}"
                )
            
            # Get neighbors in clockwise order
            for neighbor in get_neighbors_func(current[0], current[1]):
                # Calculate cost: orthogonal = 1, diagonal = sqrt(2) ≈ 1.414
                dr = abs(neighbor[0] - current[0])
                dc = abs(neighbor[1] - current[1])
                edge_cost = 1.414 if (dr == 1 and dc == 1) else 1.0
                new_cost = self.cost[current] + edge_cost
                
                if neighbor not in self.visited or new_cost < self.cost.get(neighbor, float('inf')):
                    if neighbor not in self.visited:
                        self.visited.add(neighbor)
                    self.parent[neighbor] = current
                    self.cost[neighbor] = new_cost
                    counter += 1
                    heapq.heappush(priority_queue, (new_cost, counter, neighbor))
                    
        self.status = SearchStatus.NOT_FOUND
        return SearchResult(
            path=None,
            visited_nodes=visited_order,
            frontier_nodes=frontier_history,
            steps=self.steps,
            status=self.status,
            message=f"No path found. Visited: {len(visited_order)} nodes"
        )

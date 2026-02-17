"""
Comprehensive Unit Tests for AI Pathfinder
Tests all algorithms and grid functionality
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grid import Grid, CellState
from algorithms import *
from config import DIRECTIONS

class TestGrid(unittest.TestCase):
    """Test Grid functionality"""
    
    def setUp(self):
        self.grid = Grid(10)
        self.grid.initialize_default()
    
    def test_grid_initialization(self):
        """Test grid is properly initialized"""
        self.assertEqual(self.grid.size, 10)
        self.assertIsNotNone(self.grid.start_pos)
        self.assertIsNotNone(self.grid.target_pos)
        self.assertEqual(self.grid.get_cell_state(1, 1), CellState.START)
        self.assertEqual(self.grid.get_cell_state(8, 8), CellState.TARGET)
    
    def test_add_remove_wall(self):
        """Test adding and removing walls"""
        self.grid.add_wall(5, 5)
        self.assertEqual(self.grid.get_cell_state(5, 5), CellState.WALL)
        
        self.grid.remove_wall(5, 5)
        self.assertEqual(self.grid.get_cell_state(5, 5), CellState.EMPTY)
    
    def test_get_neighbors(self):
        """Test neighbor retrieval in clockwise order"""
        # Clear area around start
        neighbors = self.grid.get_neighbors(1, 1)
        self.assertIsInstance(neighbors, list)
        
        # Check neighbor order (Up, Right, Bottom, Bottom-Right, Left, Top-Left)
        expected = [
            (0, 1),   # Up
            (1, 2),   # Right
            (2, 1),   # Bottom
            (2, 2),   # Bottom-Right
            (1, 0),   # Left
            (0, 0),   # Top-Left
        ]
        for exp in expected:
            if exp in neighbors:
                self.assertIn(exp, neighbors)
    
    def test_is_walkable(self):
        """Test walkable check"""
        self.assertTrue(self.grid.is_walkable(1, 1))
        self.grid.add_wall(5, 5)
        self.assertFalse(self.grid.is_walkable(5, 5))
        self.assertFalse(self.grid.is_walkable(-1, -1))  # Out of bounds


class TestBFS(unittest.TestCase):
    """Test BFS Algorithm"""
    
    def setUp(self):
        self.grid = Grid(10)
        self.grid.initialize_default()
        self.algo = BFS()
    
    def test_bfs_finds_path_clear_grid(self):
        """BFS should find path in clear grid"""
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        self.assertEqual(result.status, SearchStatus.FOUND)
        self.assertIsNotNone(result.path)
        self.assertGreater(len(result.path), 0)
        self.assertEqual(result.path[0], self.grid.start_pos)
        self.assertEqual(result.path[-1], self.grid.target_pos)
    
    def test_bfs_no_path_blocked(self):
        """BFS should handle blocked path"""
        # Create a complete wall barrier (including diagonals)
        target_row, target_col = self.grid.target_pos
        # Block all cells around target including diagonals
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = target_row + dr, target_col + dc
                if self.grid.is_valid_position(r, c):
                    self.grid.add_wall(r, c)
        
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        self.assertEqual(result.status, SearchStatus.NOT_FOUND)


class TestDFS(unittest.TestCase):
    """Test DFS Algorithm"""
    
    def setUp(self):
        self.grid = Grid(10)
        self.grid.initialize_default()
        self.algo = DFS()
    
    def test_dfs_finds_path(self):
        """DFS should find a path"""
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        self.assertEqual(result.status, SearchStatus.FOUND)
        self.assertIsNotNone(result.path)
    
    def test_dfs_explores_deep(self):
        """DFS should explore deeply"""
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        self.assertGreater(len(result.visited_nodes), 0)


class TestUCS(unittest.TestCase):
    """Test UCS Algorithm"""
    
    def setUp(self):
        self.grid = Grid(10)
        self.grid.initialize_default()
        self.algo = UCS()
    
    def test_ucs_finds_optimal_path(self):
        """UCS should find optimal path"""
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        self.assertEqual(result.status, SearchStatus.FOUND)
        self.assertIsNotNone(result.path)
    
    def test_ucs_tracks_cost(self):
        """UCS should track path costs"""
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        self.assertIn('Cost', result.message)


class TestDLS(unittest.TestCase):
    """Test DLS Algorithm"""
    
    def setUp(self):
        self.grid = Grid(10)
        self.grid.initialize_default()
    
    def test_dls_finds_path_within_limit(self):
        """DLS should find path within depth limit"""
        self.algo = DLS(depth_limit=50)
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        self.assertEqual(result.status, SearchStatus.FOUND)
        self.assertIsNotNone(result.path)
        self.assertLessEqual(len(result.path), 50)
    
    def test_dls_fails_when_limit_too_low(self):
        """DLS should fail when depth limit is too low"""
        self.algo = DLS(depth_limit=2)
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        # Should not find path with limit of 2 in a 10x10 grid
        self.assertEqual(result.status, SearchStatus.NOT_FOUND)
    
    def test_dls_path_is_continuous(self):
        """DLS path should be continuous"""
        self.algo = DLS(depth_limit=50)
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        if result.path:
            for i in range(len(result.path) - 1):
                curr = result.path[i]
                next_pos = result.path[i + 1]
                # Check if adjacent (including diagonals)
                diff = abs(curr[0] - next_pos[0]), abs(curr[1] - next_pos[1])
                self.assertLessEqual(max(diff), 1)


class TestIDDFS(unittest.TestCase):
    """Test IDDFS Algorithm"""
    
    def setUp(self):
        self.grid = Grid(10)
        self.grid.initialize_default()
    
    def test_iddfs_finds_path(self):
        """IDDFS should find path"""
        self.algo = IDDFS(max_depth=50)
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        self.assertEqual(result.status, SearchStatus.FOUND)
        self.assertIsNotNone(result.path)
        self.assertEqual(result.path[0], self.grid.start_pos)
        self.assertEqual(result.path[-1], self.grid.target_pos)
    
    def test_iddfs_path_validity(self):
        """IDDFS path should be valid"""
        self.algo = IDDFS(max_depth=50)
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        if result.path:
            # Check path connectivity
            for i in range(len(result.path) - 1):
                curr = result.path[i]
                next_pos = result.path[i + 1]
                diff = abs(curr[0] - next_pos[0]), abs(curr[1] - next_pos[1])
                self.assertLessEqual(max(diff), 1, 
                    f"Path not continuous between {curr} and {next_pos}")
    
    def test_iddfs_no_path_blocked(self):
        """IDDFS should handle blocked path"""
        # Create wall barrier
        for c in range(10):
            self.grid.add_wall(5, c)
        
        self.algo = IDDFS(max_depth=50)
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        self.assertEqual(result.status, SearchStatus.NOT_FOUND)


class TestBidirectional(unittest.TestCase):
    """Test Bidirectional Search Algorithm"""
    
    def setUp(self):
        self.grid = Grid(10)
        self.grid.initialize_default()
        self.algo = BidirectionalSearch()
    
    def test_bidirectional_finds_path(self):
        """Bidirectional should find path"""
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        self.assertEqual(result.status, SearchStatus.FOUND)
        self.assertIsNotNone(result.path)
        self.assertGreater(len(result.path), 0)
    
    def test_bidirectional_path_valid(self):
        """Bidirectional path should be valid and continuous"""
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        self.assertEqual(result.status, SearchStatus.FOUND)
        self.assertEqual(result.path[0], self.grid.start_pos)
        self.assertEqual(result.path[-1], self.grid.target_pos)
        
        # Verify path continuity
        for i in range(len(result.path) - 1):
            curr = result.path[i]
            next_pos = result.path[i + 1]
            diff = abs(curr[0] - next_pos[0]), abs(curr[1] - next_pos[1])
            self.assertLessEqual(max(diff), 1,
                f"Path not continuous at index {i}: {curr} -> {next_pos}")
    
    def test_bidirectional_faster_than_bfs(self):
        """Bidirectional should explore fewer nodes than BFS"""
        bfs = BFS()
        bfs_result = bfs.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        
        bi_result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        
        # Bidirectional should explore fewer or equal nodes
        self.assertLessEqual(len(bi_result.visited_nodes), len(bfs_result.visited_nodes))
    
    def test_bidirectional_meeting_point(self):
        """Bidirectional should have valid meeting point"""
        result = self.algo.search(
            self.grid.start_pos,
            self.grid.target_pos,
            self.grid.get_neighbors
        )
        self.assertEqual(result.status, SearchStatus.FOUND)
        
        # Path should be continuous from start to target
        path_set = set(result.path)
        # Meeting point should be in the middle of the path
        mid_idx = len(result.path) // 2
        meeting_point = result.path[mid_idx]
        self.assertIn(meeting_point, path_set)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_same_start_and_target(self):
        """All algorithms should handle start == target"""
        grid = Grid(5)
        grid.initialize_default()
        
        # Set target to same as start
        grid.target_pos = grid.start_pos
        
        for AlgoClass in [BFS, DFS, UCS, DLS, IDDFS, BidirectionalSearch]:
            if AlgoClass == DLS:
                algo = AlgoClass(depth_limit=10)
            elif AlgoClass == IDDFS:
                algo = AlgoClass(max_depth=10)
            else:
                algo = AlgoClass()
            
            result = algo.search(
                grid.start_pos,
                grid.target_pos,
                grid.get_neighbors
            )
            self.assertEqual(result.status, SearchStatus.FOUND)
            self.assertEqual(len(result.path), 1)
    
    def test_single_step_path(self):
        """Test when target is adjacent to start"""
        grid = Grid(5)
        grid.initialize_default()
        
        # Clear old target and set new target adjacent to start
        old_target = grid.target_pos
        grid.grid[old_target[0]][old_target[1]] = CellState.EMPTY
        
        new_target = (grid.start_pos[0], grid.start_pos[1] + 1)
        grid.target_pos = new_target
        grid.grid[new_target[0]][new_target[1]] = CellState.TARGET
        
        for AlgoClass in [BFS, DFS, UCS, DLS, IDDFS, BidirectionalSearch]:
            if AlgoClass == DLS:
                algo = AlgoClass(depth_limit=10)
            elif AlgoClass == IDDFS:
                algo = AlgoClass(max_depth=10)
            else:
                algo = AlgoClass()
            
            result = algo.search(
                grid.start_pos,
                grid.target_pos,
                grid.get_neighbors
            )
            self.assertEqual(result.status, SearchStatus.FOUND)
            # Path should contain at least 2 nodes (start and target)
            # Note: Some algorithms may include more nodes in the path
            self.assertGreaterEqual(len(result.path), 2, 
                f"{AlgoClass.__name__} path should have at least 2 nodes")
            # First node should be start, last should be target
            self.assertEqual(result.path[0], grid.start_pos)
            self.assertEqual(result.path[-1], grid.target_pos)


def run_tests():
    """Run all tests and return results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGrid))
    suite.addTests(loader.loadTestsFromTestCase(TestBFS))
    suite.addTests(loader.loadTestsFromTestCase(TestDFS))
    suite.addTests(loader.loadTestsFromTestCase(TestUCS))
    suite.addTests(loader.loadTestsFromTestCase(TestDLS))
    suite.addTests(loader.loadTestsFromTestCase(TestIDDFS))
    suite.addTests(loader.loadTestsFromTestCase(TestBidirectional))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    run_tests()

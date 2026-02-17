"""
AI Pathfinder - Main Application - ENHANCED VERSION
Grid-based search algorithm visualizer with dynamic obstacles
Comprehensive error handling and logging
"""
import sys
import os
import logging
import traceback
from typing import Optional, Tuple, Dict, Any

# Configure logging before anything else
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pathfinder.log')
    ]
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pygame
except ImportError as e:
    logger.error(f"Failed to import pygame: {e}")
    print("ERROR: pygame is required. Install with: pip install pygame")
    sys.exit(1)

from config import *
from grid import Grid, CellState
from algorithms import *
from dynamic_environment import DynamicEnvironment
from gui import Visualizer

class PathfinderApp:
    """
    Main application controller with comprehensive error handling.
    Handles user input, algorithm execution, and visualization.
    """
    
    def __init__(self):
        try:
            logger.info("Initializing Pathfinder Application...")
            self.grid = Grid(GRID_SIZE)
            self.grid.initialize_default()
            
            self.visualizer = Visualizer(self.grid)
            self.env = DynamicEnvironment(self.grid)
            
            # Algorithm instances
            self.algorithms = {
                'BFS': BFS(),
                'DFS': DFS(),
                'UCS': UCS(),
                'DLS': DLS(),
                'IDDFS': IDDFS(),
                'Bidir': BidirectionalSearch()
            }
            
            self.current_algorithm = 'BFS'
            self.current_result: Optional[SearchResult] = None
            
            # State
            self.is_running = False
            self.is_paused = False
            self.edit_mode = 'wall'
            self.animation_index = 0
            self.animation_speed = ANIMATION_DELAY
            
            # Statistics
            self.stats = {
                'Algorithm': self.current_algorithm,
                'Status': 'Idle',
                'Nodes Visited': 0,
                'Path Length': 0,
                'Steps': 0,
                'Replans': 0,
                'Dynamic Obs': 0
            }
            
            logger.info("Application initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            logger.error(traceback.format_exc())
            raise
        
    def run_algorithm(self) -> bool:
        """Run the selected search algorithm with error handling"""
        try:
            if not self.grid.start_pos or not self.grid.target_pos:
                logger.error("Start or target position not set")
                self.visualizer.show_message("Error: Start/Target not set")
                return False
            
            self.grid.clear_search_visualization()
            self.env.reset()
            
            algorithm = self.algorithms.get(self.current_algorithm)
            if not algorithm:
                logger.error(f"Unknown algorithm: {self.current_algorithm}")
                return False
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Running {algorithm.full_name}")
            logger.info(f"Start: {self.grid.start_pos}, Target: {self.grid.target_pos}")
            logger.info(f"{'='*60}\n")
            
            # Execute search with timeout protection
            result = algorithm.search(
                start=self.grid.start_pos,
                target=self.grid.target_pos,
                get_neighbors_func=self.grid.get_neighbors
            )
            
            self.current_result = result
            self.is_running = True
            self.animation_index = 0
            
            # Update stats
            self._update_stats_from_result(result)
            
            logger.info(result.message)
            
            # Show result message
            if result.status == SearchStatus.FOUND:
                self.visualizer.show_message(f"Path found! Length: {len(result.path) if result.path else 0}")
            else:
                self.visualizer.show_message("No path found!")
            
            return True
            
        except Exception as e:
            logger.error(f"Error running algorithm: {e}")
            logger.error(traceback.format_exc())
            self.visualizer.show_message(f"Error: {str(e)[:50]}")
            self.stats['Status'] = 'Error'
            return False
        
    def _update_stats_from_result(self, result: SearchResult):
        """Update statistics from search result"""
        self.stats['Algorithm'] = self.current_algorithm
        self.stats['Status'] = result.status.value
        self.stats['Nodes Visited'] = len(result.visited_nodes)
        self.stats['Path Length'] = len(result.path) if result.path else 0
        self.stats['Steps'] = result.steps
        self.stats['Replans'] = 0
        self.stats['Dynamic Obs'] = 0
        
    def animate_search(self):
        """Animate the search process step by step with error handling"""
        try:
            if not self.current_result or not ENABLE_ANIMATION:
                return
                
            if self.animation_index < len(self.current_result.visited_nodes):
                # Show visited node
                node = self.current_result.visited_nodes[self.animation_index]
                self.grid.mark_explored(node[0], node[1])
                
                # Show frontier
                if self.animation_index < len(self.current_result.frontier_nodes):
                    frontier = self.current_result.frontier_nodes[self.animation_index]
                    for f_node in frontier:
                        if self.grid.get_cell_state(f_node[0], f_node[1]) == CellState.EMPTY:
                            self.grid.mark_frontier(f_node[0], f_node[1])
                
                self.animation_index += 1
                self.stats['Nodes Visited'] = self.animation_index
                
            else:
                # Animation complete, show path
                if self.current_result.path:
                    self.grid.mark_path(self.current_result.path)
                    self.is_running = False
                    self.stats['Status'] = 'Path Found'
                else:
                    self.is_running = False
                    self.stats['Status'] = 'No Path'
                    
        except Exception as e:
            logger.error(f"Error during animation: {e}")
            logger.error(traceback.format_exc())
            self.is_running = False
            
    def check_and_replan(self):
        """Check if path is blocked and trigger replanning"""
        try:
            if not self.current_result or not self.current_result.path:
                return
                
            # Use current start position as agent position
            current_pos = self.grid.start_pos
            if not current_pos:
                return
                
            if self.env.replan_needed(self.current_result, current_pos):
                logger.info("Path blocked! Triggering replan...")
                self.visualizer.show_message("Path blocked! Replanning...")
                
                algorithm = self.algorithms.get(self.current_algorithm)
                if not algorithm:
                    return
                    
                new_result = self.env.trigger_replan(
                    current_pos=current_pos,
                    algorithm=algorithm,
                    get_neighbors_func=self.grid.get_neighbors
                )
                
                self.current_result = new_result
                self.animation_index = 0
                self.stats['Replans'] = self.env.replan_count
                self.stats['Status'] = 'Replanning'
                
                logger.info(f"Replan complete: {new_result.message}")
                
        except Exception as e:
            logger.error(f"Error during replanning: {e}")
            logger.error(traceback.format_exc())
            
    def handle_button_click(self, button: str):
        """Handle button clicks with error handling"""
        try:
            if button == 'start':
                if not self.is_running:
                    if self.run_algorithm():
                        logger.info("Algorithm started successfully")
                    
            elif button == 'pause':
                self.is_paused = not self.is_paused
                status = "paused" if self.is_paused else "resumed"
                logger.info(f"Animation {status}")
                
            elif button == 'reset':
                self.grid.reset()
                self.current_result = None
                self.is_running = False
                self.animation_index = 0
                self.stats['Status'] = 'Reset'
                self.stats['Replans'] = 0
                self.stats['Dynamic Obs'] = 0
                logger.info("Grid reset")
                
            elif button == 'clear':
                self.grid.reset()
                self.grid.clear_walls()
                self.current_result = None
                self.is_running = False
                self.stats['Status'] = 'Cleared'
                logger.info("Grid cleared")
                
            elif button.startswith('algo_'):
                algo_name = button.replace('algo_', '')
                if algo_name in self.algorithms:
                    self.current_algorithm = algo_name
                    self.stats['Algorithm'] = algo_name
                    logger.info(f"Selected algorithm: {algo_name}")
                    self.visualizer.show_message(f"Algorithm: {algo_name}")
                    
            elif button == 'random_walls':
                density = 0.25
                self.grid.randomize_walls(density)
                logger.info(f"Generated random walls with density {density}")
                self.visualizer.show_message("Random walls generated")
                
            elif button == 'clear_dynamic':
                self.grid.clear_dynamic_obstacles()
                self.stats['Dynamic Obs'] = 0
                logger.info("Dynamic obstacles cleared")
                self.visualizer.show_message("Dynamic obstacles cleared")
                
            elif button == 'speed_slow':
                self.animation_speed = 200
                self.visualizer.animation_delay = 200
                self.visualizer.show_message("Speed: Slow")
                
            elif button == 'speed_medium':
                self.animation_speed = 50
                self.visualizer.animation_delay = 50
                self.visualizer.show_message("Speed: Fast")
                
            elif button == 'mode_start':
                self.edit_mode = 'start'
                self.visualizer.current_mode = 'start'
                self.visualizer.show_message("Mode: Place Start")
                logger.info("Edit mode changed to: START")
                
            elif button == 'mode_target':
                self.edit_mode = 'target'
                self.visualizer.current_mode = 'target'
                self.visualizer.show_message("Mode: Place Target")
                logger.info("Edit mode changed to: TARGET")
                
            elif button == 'mode_wall':
                self.edit_mode = 'wall'
                self.visualizer.current_mode = 'wall'
                self.visualizer.show_message("Mode: Place Walls")
                logger.info("Edit mode changed to: WALL")
                
        except Exception as e:
            logger.error(f"Error handling button click {button}: {e}")
            logger.error(traceback.format_exc())
            
    def handle_cell_click(self, cell: Tuple[int, int]):
        """Handle grid cell clicks with error handling"""
        try:
            if not cell:
                return
                
            row, col = cell
            current_state = self.grid.get_cell_state(row, col)
            
            if self.edit_mode == 'start':
                # Place start node
                if current_state not in [CellState.TARGET, CellState.WALL]:
                    if self.grid.set_start(row, col):
                        logger.info(f"Start position set to ({row}, {col})")
                        self.visualizer.show_message(f"Start: ({row}, {col})")
                        
            elif self.edit_mode == 'target':
                # Place target node
                if current_state not in [CellState.START, CellState.WALL]:
                    if self.grid.set_target(row, col):
                        logger.info(f"Target position set to ({row}, {col})")
                        self.visualizer.show_message(f"Target: ({row}, {col})")
                        
            elif self.edit_mode == 'wall':
                # Toggle walls
                if current_state == CellState.START:
                    return
                elif current_state == CellState.TARGET:
                    return
                elif current_state == CellState.WALL:
                    self.grid.remove_wall(row, col)
                    logger.debug(f"Removed wall at ({row}, {col})")
                elif current_state == CellState.EMPTY:
                    self.grid.add_wall(row, col)
                    logger.debug(f"Added wall at ({row}, {col})")
                
        except Exception as e:
            logger.error(f"Error handling cell click: {e}")
            logger.error(traceback.format_exc())
            
    def update(self):
        """Main update loop with error handling"""
        try:
            if self.is_running and not self.is_paused:
                self.animate_search()
                
            # Check for dynamic obstacles and replanning
            if self.is_running:
                self.check_and_replan()
                
        except Exception as e:
            logger.error(f"Error in update loop: {e}")
            logger.error(traceback.format_exc())
            
    def draw(self):
        """Render the application"""
        try:
            self.visualizer.render(
                algorithm_name=self.current_algorithm,
                stats=self.stats,
                is_running=self.is_running,
                is_paused=self.is_paused
            )
        except Exception as e:
            logger.error(f"Error in draw: {e}")
            logger.error(traceback.format_exc())
            
    def run(self):
        """Main application loop with comprehensive error handling"""
        logger.info("\n" + "="*60)
        logger.info("  AI Pathfinder - Grid Search Visualizer")
        logger.info("  " + WINDOW_TITLE)
        logger.info("="*60)
        logger.info("\nControls:")
        logger.info("  - Click cells to add/remove walls")
        logger.info("  - Click algorithm buttons to select")
        logger.info("  - START button to begin search")
        logger.info("  - SPACE to pause/resume")
        logger.info("  - R to reset, C to clear all")
        logger.info("  - Check pathfinder.log for detailed logs\n")
        
        running = True
        
        try:
            while running:
                # Handle events
                try:
                    actions = self.visualizer.handle_events()
                except Exception as e:
                    logger.error(f"Error handling events: {e}")
                    actions = []
                
                for action, data in actions:
                    if action == 'quit':
                        running = False
                        logger.info("Quit requested by user")
                    elif action == 'button_click':
                        self.handle_button_click(data)
                    elif action == 'cell_click':
                        self.handle_cell_click(data)
                    elif action == 'key_press':
                        if data == 'space':
                            self.is_paused = not self.is_paused
                        elif data == 'r':
                            self.handle_button_click('reset')
                        elif data == 'c':
                            self.handle_button_click('clear')
                        elif data == 'p':
                            self.is_paused = not self.is_paused
                        elif data == 's':
                            if not self.is_running:
                                self.run_algorithm()
                            
                # Update
                self.update()
                
                # Draw
                self.draw()
                
        except KeyboardInterrupt:
            logger.info("\nInterrupted by user (Ctrl+C)")
        except Exception as e:
            logger.error(f"Fatal error in main loop: {e}")
            logger.error(traceback.format_exc())
            print(f"\nFatal error: {e}")
            print("Check pathfinder.log for details")
        finally:
            try:
                self.visualizer.quit()
                logger.info("Application closed successfully")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    try:
        app = PathfinderApp()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        logger.error(traceback.format_exc())
        print(f"Failed to start: {e}")
        print("Check pathfinder.log for details")
        sys.exit(1)

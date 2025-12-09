from dataclasses import dataclass
import time


@dataclass
class Robot:

    # Simple warehouse robot model 
    max_load: float = 50.0   # kilograms

    # Operational state
    x: int = 0               # grid position
    y: int = 0
    status: str = "idle"     # idle, moving, loading, etc.

    # Task fields
    current_task: str = ""   # task label or order ID
    target_x: int = 0        # destination x
    target_y: int = 0        # destination y

    # Error flag
    error_flag: bool = False

   
    
    # Helper Methods
    def get_position(self):
        return (self.x, self.y)

    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy

    def set_status(self, new_status: str):
        self.status = new_status

    def set_task(self, task_name: str, target_x: int, target_y: int):
        self.current_task = task_name
        self.target_x = target_x
        self.target_y = target_y

    def clear_task(self):
        self.current_task = ""
        self.target_x = 0
        self.target_y = 0

    def distance_to(self, x: int, y: int):
        return abs(self.x - x) + abs(self.y - y)

    def is_idle(self):
        return self.status == "idle"

    def mark_error(self, message: str = "Unknown error"):
        self.error_flag = True
        self.status = "error"
        print(f"[ERROR] Robot: {message}")

    def reset_error(self):
        self.error_flag = False
        self.status = "idle"

    def at_target(self):
        return self.x == self.target_x and self.y == self.target_y

    def get_state(self):
        return {
            "x": self.x,
            "y": self.y,
            "status": self.status,
            "task": self.current_task,
            "target": (self.target_x, self.target_y),
            "error": self.error_flag,
        }
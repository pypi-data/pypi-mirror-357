"""Main DOF class for the robotics framework."""

import subprocess
from typing import Optional
from .executors.isaac_sim import IsaacSimExecutor


class DOF:
    """Main DOF class for robotics operations."""
    
    def __init__(self):
        """Initialize the DOF framework."""
        self.simulator = None
    
    def start_sim(self) -> IsaacSimExecutor:
        """Start Isaac Sim and open VS Code with the container connection.
        
        Returns:
            IsaacSimExecutor: The initialized Isaac Sim executor
        """
        # Step 1 - Define the container URI for VS Code
        container_uri = ("vscode-remote://ssh-remote+isaac-ec2"
                        "/home/ubuntu/docker/isaac-sim/documents")
        
        # Step 2 – open / reuse VS Code window on the container
        subprocess.call(["code", "--reuse-window", "--folder-uri", container_uri])
        
        # Initialize and return the Isaac Sim executor
        self.simulator = IsaacSimExecutor()
        return self.simulator
    
    def get_simulator(self) -> Optional[IsaacSimExecutor]:
        """Get the current simulator instance if it exists.
        
        Returns:
            IsaacSimExecutor or None: The current simulator instance
        """
        return self.simulator 
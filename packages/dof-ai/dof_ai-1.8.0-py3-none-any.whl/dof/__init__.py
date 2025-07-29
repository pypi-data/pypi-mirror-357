"""Top-level package for dof - LangChain for Robotics."""

# Main DOF class
from .main import DOF

# Core framework
from .core import Chain
from .actions import Robot
from .executors import SimulatorExecutor, BaseRobotExecutor, IsaacSimExecutor

# Legacy functions for backward compatibility
from .dof import robot_hello, chain_robot_actions

__author__ = """Pieter Becking"""
__email__ = "ph.becking@gmail.com"
__version__ = "0.1.1"

__all__ = [
    # Main DOF class
    "DOF",
    # New framework
    "Chain",
    "Robot",
    "SimulatorExecutor",
    "BaseRobotExecutor",
    "IsaacSimExecutor",
    # Legacy
    "robot_hello",
    "chain_robot_actions",
]

"""
PyInGraph 🐷 - A Python-based framework for graphically integrating multiple Python algorithms
"""

__version__ = "0.1.0"
__author__ = "bobobone"
__email__ = "bobobone@qq.com"

from .PyG_graph_load import GraphLoader
from .PyG_node_interface import BlockBase

__all__ = [
    'GraphLoader',
    'BlockBase', 
]
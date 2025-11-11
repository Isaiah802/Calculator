"""
Graphing Module - Unified Graphing Interface for Peanut 3000 Calculator
========================================================================

This module provides a unified interface to all graphing capabilities
of the calculator, including:
- 2D function plotting
- Statistical visualization (histograms, scatter plots, box plots)
- Complex number plotting
- 3D surface rendering
- Interactive graph controls (zoom, pan, trace)

The GraphManager class wraps existing graphics engines and provides
a simplified API for common graphing operations.

Classes:
    GraphManager: Unified graph management interface

Functions:
    create_graph_manager: Factory function to create GraphManager

Example:
    >>> from graphing import GraphManager
    >>> graph_mgr = GraphManager(display_manager)
    >>> graph_mgr.plot_function("sin(x)", -10, 10)
"""

from .graph_manager import GraphManager, create_graph_manager

__all__ = ['GraphManager', 'create_graph_manager']

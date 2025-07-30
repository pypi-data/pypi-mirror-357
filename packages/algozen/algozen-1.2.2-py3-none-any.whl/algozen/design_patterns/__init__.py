"""
Design Patterns Module

This module contains implementations of common design patterns.
"""

from algozen.design_patterns.chain_of_responsibility import *
from algozen.design_patterns.command import *
from algozen.design_patterns.decorator import *
from algozen.design_patterns.factory import *
from algozen.design_patterns.iterator import *
from algozen.design_patterns.observer import *
from algozen.design_patterns.state import *
from algozen.design_patterns.strategy import *
from algozen.design_patterns.template_method import *

__all__ = []

# Collect all exports from submodules
for module_name in [
    'chain_of_responsibility', 'command', 'decorator', 'factory',
    'iterator', 'observer', 'state', 'strategy', 'template_method'
]:
    try:
        module = __import__(f'algozen.design_patterns.{module_name}', fromlist=['*'])
        if hasattr(module, '__all__'):
            __all__.extend(module.__all__)
        else:
            __all__.extend([name for name in dir(module) if not name.startswith('_')])
    except ImportError:
        pass

__all__ = list(dict.fromkeys(__all__))  # Remove duplicates
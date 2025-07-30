"""
Decorator Pattern Implementation.

This module provides an implementation of the Decorator pattern, which allows
behavior to be added to individual objects dynamically, without affecting the
behavior of other objects from the same class.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, TypeVar, Generic, Type, cast
import time
import functools
import logging

T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

class Component(ABC):
    """
    The Component interface defines operations that can be altered by decorators.
    """
    @abstractmethod
    def operation(self) -> str:
        """
        The base operation that can be modified by decorators.
        
        Returns:
            A string representing the result of the operation.
        """
        pass

class ConcreteComponent(Component):
    """
    Concrete Components provide default implementations of the operations.
    """
    def operation(self) -> str:
        """
        Perform the base operation.
        
        Returns:
            A string representing the result of the operation.
        """
        return "ConcreteComponent: Basic operation"

class Decorator(Component, ABC):
    """
    The base Decorator class follows the same interface as the Component.
    The primary purpose of this class is to define the wrapping interface for
    all concrete decorators.
    """
    def __init__(self, component: Component) -> None:
        """
        Initialize the decorator with a component.
        
        Args:
            component: The component to be decorated.
        """
        self._component = component
    
    @property
    def component(self) -> Component:
        """
        Get the wrapped component.
        
        Returns:
            The wrapped component instance.
        """
        return self._component
    
    def operation(self) -> str:
        """
        Delegate the work to the wrapped component.
        
        Returns:
            The result of the component's operation.
        """
        return self._component.operation()

class ConcreteDecoratorA(Decorator):
    """
    Concrete Decorator that adds behavior before and/or after calling the
    wrapped component.
    """
    def operation(self) -> str:
        """
        Execute the decorator's behavior and then delegate to the wrapped component.
        
        Returns:
            The decorated result of the component's operation.
        """
        return f"ConcreteDecoratorA({self.component.operation()})"

class ConcreteDecoratorB(Decorator):
    """
    Another concrete decorator that adds different behavior.
    """
    def operation(self) -> str:
        """
        Execute the decorator's behavior and then delegate to the wrapped component.
        
        Returns:
            The decorated result of the component's operation.
        """
        return f"ConcreteDecoratorB({self.component.operation()})"

# ============================================
# Function Decorators
# ============================================

def timer(func: F) -> F:
    """
    A decorator that measures the execution time of a function.
    
    Args:
        func: The function to be decorated.
        
    Returns:
        The decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result
    return cast(F, wrapper)

def log_call(logger: Optional[logging.Logger] = None) -> Callable[[F], F]:
    """
    A decorator factory that logs function calls and their results.
    
    Args:
        logger: Optional logger instance. If not provided, uses the root logger.
        
    Returns:
        A decorator function.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            log = logger or logging.getLogger(func.__module__)
            log.debug("Calling %s with args=%s, kwargs=%s", 
                     func.__name__, args, kwargs)
            try:
                result = func(*args, **kwargs)
                log.debug("%s returned %s", func.__name__, result)
                return result
            except Exception as e:
                log.exception("%s raised %s", func.__name__, str(e))
                raise
        return cast(F, wrapper)
    return decorator

class RetryDecorator:
    """
    A decorator that retries a function call if it raises an exception.
    """
    def __init__(self, 
                max_retries: int = 3, 
                delay: float = 1.0,
                exceptions: Type[Exception] | tuple[Type[Exception], ...] = Exception):
        """
        Initialize the retry decorator.
        
        Args:
            max_retries: Maximum number of retry attempts.
            delay: Delay between retries in seconds.
            exceptions: Exception type(s) to catch and retry on.
        """
        self.max_retries = max_retries
        self.delay = delay
        self.exceptions = exceptions
    
    def __call__(self, func: F) -> F:
        """
        Decorate the function with retry logic.
        
        Args:
            func: The function to decorate.
            
        Returns:
            The decorated function.
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except self.exceptions as e:
                    last_exception = e
                    if attempt < self.max_retries:
                        time.sleep(self.delay * (attempt + 1))
            
            raise last_exception  # type: ignore
        
        return cast(F, wrapper)

# ============================================
# Property Decorators
# ============================================

def validate_type(prop_type: Type[T]) -> Callable[[F], property]:
    """
    A decorator factory that validates the type of a property.
    
    Args:
        prop_type: The expected type of the property.
        
    Returns:
        A property decorator that performs type validation.
    """
    def decorator(func: F) -> property:
        @property
        def wrapper(self: Any) -> T:
            value = func(self)
            if not isinstance(value, prop_type):
                raise TypeError(
                    f"Expected {func.__name__} to be of type {prop_type.__name__}, "
                    f"got {type(value).__name__}"
                )
            return value
        
        @wrapper.setter
        def wrapper(self: Any, value: T) -> None:
            if not isinstance(value, prop_type):
                raise TypeError(
                    f"Expected {func.__name__} to be of type {prop_type.__name__}, "
                    f"got {type(value).__name__}"
                )
            # Store the value in a private variable
            setattr(self, f"_{func.__name__}", value)
        
        # Initialize the property
        return wrapper
    return decorator

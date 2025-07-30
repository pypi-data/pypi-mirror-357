"""
Chain of Responsibility Pattern Implementation.

This module provides an implementation of the Chain of Responsibility pattern,
which lets you pass requests along a chain of handlers. Upon receiving a request,
each handler decides either to process the request or to pass it to the next
handler in the chain.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional, TypeVar, Generic, Dict, List
import re
import json
from dataclasses import dataclass

T = TypeVar('T')

class Handler(ABC, Generic[T]):
    """
    The Handler interface declares a method for building the chain of handlers.
    It also declares a method for executing a request.
    """
    _next_handler: Optional['Handler[T]'] = None
    
    def set_next(self, handler: 'Handler[T]') -> 'Handler[T]':
        """
        Set the next handler in the chain.
        
        Args:
            handler: The next handler in the chain.
            
        Returns:
            The next handler (for method chaining).
        """
        self._next_handler = handler
        return handler
    
    @abstractmethod
    def handle(self, request: T) -> Optional[Any]:
        """
        Handle the request or pass it to the next handler in the chain.
        
        Args:
            request: The request to handle.
            
        Returns:
            The result of handling the request, or None if the request wasn't handled.
        """
        if self._next_handler:
            return self._next_handler.handle(request)
        return None

@dataclass
class Request:
    """
    A simple request object that carries some data.
    """
    data: Dict[str, Any]
    headers: Dict[str, str]
    user: Optional[Dict[str, Any]] = None

class AuthenticationHandler(Handler[Request]):
    """
    Concrete handler for authentication.
    """
    def handle(self, request: Request) -> Optional[Any]:
        """
        Handle authentication.
        
        Args:
            request: The request to handle.
            
        Returns:
            The result of the next handler or an error if authentication fails.
            
        Raises:
            PermissionError: If authentication fails.
        """
        if not request.user or 'id' not in request.user:
            raise PermissionError("Authentication required")
        print("AuthenticationHandler: User authenticated")
        return super().handle(request)

class ValidationHandler(Handler[Request]):
    """
    Concrete handler for request validation.
    """
    def handle(self, request: Request) -> Optional[Any]:
        """
        Validate the request data.
        
        Args:
            request: The request to validate.
            
        Returns:
            The result of the next handler or an error if validation fails.
            
        Raises:
            ValueError: If the request data is invalid.
        """
        if not request.data or not isinstance(request.data, dict):
            raise ValueError("Invalid request data")
        print("ValidationHandler: Request data is valid")
        return super().handle(request)

class LoggingHandler(Handler[Request]):
    """
    Concrete handler for request logging.
    """
    def handle(self, request: Request) -> Optional[Any]:
        """
        Log the request.
        
        Args:
            request: The request to log.
            
        Returns:
            The result of the next handler.
        """
        print(f"LoggingHandler: Processing request from user {request.user.get('id', 'unknown')}")
        return super().handle(request)

class ProcessingHandler(Handler[Request]):
    """
    Concrete handler that processes the request.
    """
    def handle(self, request: Request) -> Dict[str, Any]:
        """
        Process the request.
        
        Args:
            request: The request to process.
            
        Returns:
            The result of processing the request.
        """
        print("ProcessingHandler: Processing request")
        return {"status": "success", "message": "Request processed successfully"}

# ============================================
# Practical Example: Log Level Handler
# ============================================

from enum import Enum, auto

class LogLevel(Enum):
    """Log levels for the logging system."""
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

@dataclass
class LogMessage:
    """A log message with a level and content."""
    level: LogLevel
    message: str
    timestamp: float = 0.0
    context: Optional[Dict[str, Any]] = None

class LogHandler(ABC):
    """
    Abstract base class for log handlers in the chain of responsibility.
    """
    _next_handler: Optional['LogHandler'] = None
    
    def set_next(self, handler: 'LogHandler') -> 'LogHandler':
        """
        Set the next handler in the chain.
        
        Args:
            handler: The next log handler.
            
        Returns:
            The next handler (for method chaining).
        """
        self._next_handler = handler
        return handler
    
    def handle(self, log_message: LogMessage) -> None:
        """
        Handle the log message or pass it to the next handler.
        
        Args:
            log_message: The log message to handle.
        """
        if self._should_handle(log_message):
            self._write_log(log_message)
        
        if self._next_handler is not None:
            self._next_handler.handle(log_message)
    
    @abstractmethod
    def _should_handle(self, log_message: LogMessage) -> bool:
        """
        Determine if this handler should handle the log message.
        
        Args:
            log_message: The log message to check.
            
        Returns:
            True if this handler should handle the message, False otherwise.
        """
        pass
    
    @abstractmethod
    def _write_log(self, log_message: LogMessage) -> None:
        """
        Write the log message.
        
        Args:
            log_message: The log message to write.
        """
        pass

class ConsoleLogHandler(LogHandler):
    """
    Log handler that writes log messages to the console.
    """
    def _should_handle(self, log_message: LogMessage) -> bool:
        return log_message.level in [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING]
    
    def _write_log(self, log_message: LogMessage) -> None:
        print(f"[Console] {log_message.level.name}: {log_message.message}")

class FileLogHandler(LogHandler):
    """
    Log handler that writes error and critical log messages to a file.
    """
    def __init__(self, filename: str = 'error.log'):
        self._filename = filename
    
    def _should_handle(self, log_message: LogMessage) -> bool:
        return log_message.level in [LogLevel.ERROR, LogLevel.CRITICAL]
    
    def _write_log(self, log_message: LogMessage) -> None:
        with open(self._filename, 'a') as f:
            f.write(f"{log_message.level.name}: {log_message.message}\n")

class EmailLogHandler(LogHandler):
    """
    Log handler that sends critical log messages via email.
    """
    def _should_handle(self, log_message: LogMessage) -> bool:
        return log_message.level == LogLevel.CRITICAL
    
    def _write_log(self, log_message: LogMessage) -> None:
        # In a real implementation, this would send an email
        print(f"[Email] CRITICAL: {log_message.message}")
        if log_message.context:
            print(f"Context: {json.dumps(log_message.context, indent=2)}")

# ============================================
# Practical Example: Request Processing Pipeline
# ============================================

class RequestHandler(ABC):
    """
    Abstract base class for request handlers in the pipeline.
    """
    _next_handler: Optional['RequestHandler'] = None
    
    def set_next(self, handler: 'RequestHandler') -> 'RequestHandler':
        """
        Set the next handler in the pipeline.
        
        Args:
            handler: The next request handler.
            
        Returns:
            The next handler (for method chaining).
        """
        self._next_handler = handler
        return handler
    
    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the request or pass it to the next handler.
        
        Args:
            request: The request to handle.
            
        Returns:
            The processed response.
            
        Raises:
            Exception: If the request cannot be processed.
        """
        if self._can_handle(request):
            return self._process_request(request)
        elif self._next_handler:
            return self._next_handler.handle(request)
        else:
            raise Exception("No handler available for the request")
    
    @abstractmethod
    def _can_handle(self, request: Dict[str, Any]) -> bool:
        """
        Determine if this handler can process the request.
        
        Args:
            request: The request to check.
            
        Returns:
            True if this handler can process the request, False otherwise.
        """
        pass
    
    @abstractmethod
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the request.
        
        Args:
            request: The request to process.
            
        Returns:
            The processed response.
            
        Raises:
            Exception: If the request cannot be processed.
        """
        pass

class AuthenticationRequestHandler(RequestHandler):
    """
    Request handler for authentication.
    """
    def _can_handle(self, request: Dict[str, Any]) -> bool:
        return 'auth' in request.get('path', '')
    
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if not request.get('token'):
            raise Exception("Authentication required")
        
        # In a real implementation, validate the token
        return {"status": "authenticated", "user_id": "user123"}

class ValidationRequestHandler(RequestHandler):
    """
    Request handler for input validation.
    """
    def _can_handle(self, request: Dict[str, Any]) -> bool:
        return 'data' in request
    
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        data = request.get('data', {})
        if not isinstance(data, dict):
            raise Exception("Invalid data format")
        
        # Add validation logic here
        return {"status": "valid", "data": data}

class ProcessingRequestHandler(RequestHandler):
    """
    Request handler for processing the main business logic.
    """
    def _can_handle(self, request: Dict[str, Any]) -> bool:
        return 'action' in request
    
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get('action')
        if action == 'get_user':
            return {"status": "success", "user": {"id": "user123", "name": "John Doe"}}
        elif action == 'get_orders':
            return {"status": "success", "orders": ["order1", "order2"]}
        else:
            raise Exception(f"Unknown action: {action}")

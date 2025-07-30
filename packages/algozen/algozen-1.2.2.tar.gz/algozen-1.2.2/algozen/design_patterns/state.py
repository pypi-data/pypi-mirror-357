"""
State Pattern Implementation.

This module provides an implementation of the State pattern, which allows an object
to alter its behavior when its internal state changes, making it appear as if the
object changed its class.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar, Generic, cast
import logging

T = TypeVar('T', bound='Context')

class State(ABC, Generic[T]):
    """
    The base State class declares methods that all Concrete State should
    implement and also provides a backreference to the Context object.
    """
    _context: Optional[T] = None
    
    @property
    def context(self) -> Optional[T]:
        """
        Get the context associated with this state.
        
        Returns:
            The context object associated with this state, or None if not set.
        """
        return self._context
    
    @context.setter
    def context(self, context: Optional[T]) -> None:
        """
        Set the context for this state.
        
        Args:
            context: The context object to associate with this state.
        """
        self._context = context
    
    @abstractmethod
    def handle1(self) -> None:
        """Handle the first state-specific request."""
        pass
    
    @abstractmethod
    def handle2(self) -> None:
        """Handle the second state-specific request."""
        pass

class ConcreteStateA(State[T]):
    """
    Concrete States implement various behaviors, associated with a state of the Context.
    """
    def handle1(self) -> None:
        """
        Handle the first request and transition to another state.
        """
        logging.info("ConcreteStateA handles request1.")
        logging.info("ConcreteStateA wants to change the state of the context.")
        if self.context:
            self.context.transition_to(ConcreteStateB())
    
    def handle2(self) -> None:
        """
        Handle the second request.
        """
        logging.info("ConcreteStateA handles request2.")

class ConcreteStateB(State[T]):
    """
    Concrete States implement various behaviors, associated with a state of the Context.
    """
    def handle1(self) -> None:
        """
        Handle the first request.
        """
        logging.info("ConcreteStateB handles request1.")
    
    def handle2(self) -> None:
        """
        Handle the second request and transition to another state.
        """
        logging.info("ConcreteStateB handles request2.")
        logging.info("ConcreteStateB wants to change the state of the context.")
        if self.context:
            self.context.transition_to(ConcreteStateA())

class Context(Generic[T]):
    """
    The Context defines the interface of interest to clients. It maintains a
    reference to an instance of a State subclass, which represents the current
    state of the Context.
    """
    def __init__(self, state: State[T]) -> None:
        """
        Initialize the context with an initial state.
        
        Args:
            state: The initial state of the context.
        """
        self._state: Optional[State[T]] = None
        self.transition_to(state)
    
    def transition_to(self, state: State[T]) -> None:
        """
        The Context allows changing the State object at runtime.
        
        Args:
            state: The new state to transition to.
        """
        logging.info(f"Context: Transition to {type(state).__name__}")
        if self._state is not None:
            self._state.context = None
        self._state = state
        if self._state is not None:
            self._state.context = self
    
    def request1(self) -> None:
        """
        The Context delegates part of its behavior to the current State object.
        """
        if self._state is not None:
            self._state.handle1()
    
    def request2(self) -> None:
        """
        The Context delegates part of its behavior to the current State object.
        """
        if self._state is not None:
            self._state.handle2()

# ============================================
# Practical Example: Document Workflow
# ============================================

class DocumentState(ABC):
    """
    The base State class for document workflow states.
    """
    @abstractmethod
    def render(self) -> None:
        """Render the document in the current state."""
        pass
    
    @abstractmethod
    def publish(self) -> None:
        """Publish the document in the current state."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the state."""
        pass

class Draft(DocumentState):
    """
    Concrete State representing a document in draft state.
    """
    def render(self) -> None:
        print("Rendering draft document (only visible to authors)")
    
    def publish(self) -> None:
        print("Publishing draft document for review")
    
    def get_name(self) -> str:
        return "Draft"

class Moderation(DocumentState):
    """
    Concrete State representing a document in moderation state.
    """
    def render(self) -> None:
        print("Rendering document in moderation (visible to moderators)")
    
    def publish(self) -> None:
        print("Publishing document after moderation")
    
    def get_name(self) -> str:
        return "Moderation"

class Published(DocumentState):
    """
    Concrete State representing a published document.
    """
    def render(self) -> None:
        print("Rendering published document (visible to everyone)")
    
    def publish(self) -> None:
        print("Document is already published")
    
    def get_name(self) -> str:
        return "Published"

class Document:
    """
    The Context class for the Document workflow example.
    """
    _state: Optional[DocumentState] = None
    
    def __init__(self) -> None:
        self.transition_to(Draft())
    
    def transition_to(self, state: DocumentState) -> None:
        """
        Transition to a new state.
        
        Args:
            state: The new state to transition to.
        """
        print(f"Document: Transitioning to {state.get_name()}")
        self._state = state
    
    def render(self) -> None:
        """Render the document in its current state."""
        if self._state is not None:
            self._state.render()
    
    def publish(self) -> None:
        """Publish the document in its current state."""
        if self._state is not None:
            self._state.publish()
    
    def next_state(self) -> None:
        """Transition to the next state in the workflow."""
        if isinstance(self._state, Draft):
            self.transition_to(Moderation())
        elif isinstance(self._state, Moderation):
            self.transition_to(Published())
        elif isinstance(self._state, Published):
            print("Document is already in the final state")

# ============================================
# Thread-Safe State Machine
# ============================================

import threading
from typing import Callable, Dict, Type, Any

class StateMachine:
    """
    A thread-safe state machine implementation.
    """
    def __init__(self, initial_state: str) -> None:
        """
        Initialize the state machine with an initial state.
        
        Args:
            initial_state: The initial state of the state machine.
        """
        self._state = initial_state
        self._transitions: Dict[str, Dict[str, str]] = {}
        self._handlers: Dict[str, Dict[str, Callable[[], None]]] = {}
        self._lock = threading.RLock()
    
    def add_transition(self, from_state: str, to_state: str, event: str) -> None:
        """
        Add a transition between states.
        
        Args:
            from_state: The source state.
            to_state: The target state.
            event: The event that triggers the transition.
        """
        with self._lock:
            if from_state not in self._transitions:
                self._transitions[from_state] = {}
            self._transitions[from_state][event] = to_state
    
    def add_handler(self, state: str, event: str, handler: Callable[[], None]) -> None:
        """
        Add an event handler for a specific state.
        
        Args:
            state: The state in which the handler should be active.
            event: The event that triggers the handler.
            handler: The handler function to call.
        """
        with self._lock:
            if state not in self._handlers:
                self._handlers[state] = {}
            self._handlers[state][event] = handler
    
    def process_event(self, event: str) -> bool:
        """
        Process an event and transition to a new state if applicable.
        
        Args:
            event: The event to process.
            
        Returns:
            True if the event was processed, False otherwise.
        """
        with self._lock:
            current_state = self._state
            
            # Check if there's a transition for this event
            if (current_state in self._transitions and 
                event in self._transitions[current_state]):
                
                # Call exit handler for current state if it exists
                if (current_state in self._handlers and 
                    'exit' in self._handlers[current_state]):
                    self._handlers[current_state]['exit']()
                
                # Transition to new state
                new_state = self._transitions[current_state][event]
                self._state = new_state
                
                # Call entry handler for new state if it exists
                if (new_state in self._handlers and 
                    'entry' in self._handlers[new_state]):
                    self._handlers[new_state]['entry']()
                
                return True
            
            # Check if there's a handler for this event in the current state
            if (current_state in self._handlers and 
                event in self._handlers[current_state]):
                self._handlers[current_state][event]()
                return True
            
            return False
    
    def get_state(self) -> str:
        """
        Get the current state of the state machine.
        
        Returns:
            The current state.
        """
        with self._lock:
            return self._state
    
    def is_in_state(self, state: str) -> bool:
        """
        Check if the state machine is in a specific state.
        
        Args:
            state: The state to check.
            
        Returns:
            True if the state machine is in the specified state, False otherwise.
        """
        with self._lock:
            return self._state == state

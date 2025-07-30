"""
Observer Pattern Implementation.

This module provides a thread-safe implementation of the Observer pattern,
which allows objects to notify other objects about changes in their state.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generic, TypeVar, Optional
import threading
import time
from dataclasses import dataclass
from datetime import datetime

T = TypeVar('T')

class Observer(Generic[T], ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """
    @abstractmethod
    def update(self, subject: T, event: str, data: Any = None) -> None:
        """
        Receive update from subject.
        
        Args:
            subject: The subject that triggered the update.
            event: A string identifying the type of event.
            data: Optional data associated with the event.
        """
        pass

class Subject(Generic[T], ABC):
    """
    The Subject interface declares methods for managing observers.
    """
    def __init__(self) -> None:
        self._observers: List[Observer[T]] = []
        self._lock = threading.Lock()
    
    def attach(self, observer: Observer[T]) -> None:
        """
        Attach an observer to the subject.
        
        Args:
            observer: The observer to attach.
        """
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)
    
    def detach(self, observer: Observer[T]) -> None:
        """
        Detach an observer from the subject.
        
        Args:
            observer: The observer to detach.
        """
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
    
    def notify(self, event: str, data: Any = None) -> None:
        """
        Notify all observers about an event.
        
        Args:
            event: A string identifying the type of event.
            data: Optional data associated with the event.
        """
        with self._lock:
            observers = self._observers.copy()
        
        for observer in observers:
            try:
                observer.update(self, event, data)
            except Exception as e:
                # Log error but don't crash the notification
                pass

class Event:
    """
    A simple class to represent an event with a type and data.
    """
    def __init__(self, event_type: str, data: Any = None):
        """
        Initialize an event.
        
        Args:
            event_type: A string identifying the type of event.
            data: Optional data associated with the event.
        """
        self.event_type = event_type
        self.data = data
        self.timestamp = time.time()
    
    def __str__(self) -> str:
        """Return a string representation of the event."""
        time_str = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return f"[{time_str}] {self.event_type}: {self.data}"

class Observable(Subject['Observable']):
    """
    A concrete implementation of Subject that can be used as a base class
    or composed into other classes to add observable behavior.
    """
    def __init__(self) -> None:
        super().__init__()
        self._event_history: List[Event] = []
    
    def notify(self, event: str, data: Any = None) -> None:
        """
        Notify all observers about an event and log it.
        
        Args:
            event: A string identifying the type of event.
            data: Optional data associated with the event.
        """
        event_obj = Event(event, data)
        with self._lock:
            self._event_history.append(event_obj)
        super().notify(event, data)
    
    def get_event_history(self) -> List[Event]:
        """
        Get a copy of the event history.
        
        Returns:
            A list of all events that have occurred.
        """
        with self._lock:
            return self._event_history.copy()
    
    def clear_event_history(self) -> None:
        """Clear the event history."""
        with self._lock:
            self._event_history.clear()

class ConcreteObserver(Observer['Observable']):
    """
    A concrete observer implementation for testing purposes.
    """
    def __init__(self, name: str):
        self.name = name
        self.received_events = []
    
    def update(self, subject: 'Observable', event: str, data: Any = None) -> None:
        """Handle updates from the subject."""
        self.received_events.append((event, data))
        print(f"{self.name} received event: {event} with data: {data}")

# Alias for backward compatibility
Observer = ConcreteObserver
Subject = Observable

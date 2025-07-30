"""
Command Pattern Implementation.

This module provides an implementation of the Command pattern, which encapsulates
a request as an object, thereby allowing for parameterization of clients with
different requests, queuing of requests, and support for undoable operations.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional, TypeVar, Generic, Callable
import json
import os

T = TypeVar('T')

class Command(ABC):
    """
    The Command interface declares a method for executing a command.
    """
    @abstractmethod
    def execute(self) -> None:
        """
        Execute the command.
        """
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """
        Undo the command and restore the previous state.
        """
        pass

class SimpleCommand(Command):
    """
    Simple commands that delegate execution to a function.
    """
    def __init__(self, payload: str) -> None:
        """
        Initialize with a payload string.
        
        Args:
            payload: A string payload for the command.
        """
        self._payload = payload
    
    def execute(self) -> None:
        """
        Execute the simple command.
        """
        print(f"SimpleCommand: Executing {self._payload}")
    
    def undo(self) -> None:
        """
        Undo the simple command.
        """
        print(f"SimpleCommand: Undoing {self._payload}")

class ComplexCommand(Command):
    """
    Complex commands can accept receiver objects along with any context data.
    """
    def __init__(self, receiver: 'Receiver', a: str, b: str) -> None:
        """
        Initialize with a receiver and context data.
        
        Args:
            receiver: The receiver object that knows how to perform the operation.
            a: First context data.
            b: Second context data.
        """
        self._receiver = receiver
        self._a = a
        self._b = b
        self._backup: Optional[str] = None
    
    def execute(self) -> None:
        """
        Execute the complex command.
        """
        print("ComplexCommand: Executing complex operation")
        self._backup = self._receiver.backup()
        self._receiver.do_something(self._a)
        self._receiver.do_something_else(self._b)
    
    def undo(self) -> None:
        """
        Undo the complex command.
        """
        if self._backup is not None:
            print("ComplexCommand: Undoing complex operation")
            self._receiver.restore(self._backup)

class Receiver:
    """
    The Receiver class contains important business logic and knows how to
    perform various operations.
    """
    def do_something(self, a: str) -> None:
        """
        Perform an operation.
        
        Args:
            a: Operation parameter.
        """
        print(f"Receiver: Working on ({a}.)")
    
    def do_something_else(self, b: str) -> None:
        """
        Perform another operation.
        
        Args:
            b: Operation parameter.
        """
        print(f"Receiver: Also working on ({b}.)")
    
    def backup(self) -> str:
        """
        Create a backup of the current state.
        
        Returns:
            A string representation of the current state.
        """
        return "Current state backup"
    
    def restore(self, state: str) -> None:
        """
        Restore state from a backup.
        
        Args:
            state: The state to restore from.
        """
        print(f"Receiver: Restoring state: {state}")

class Invoker:
    """
    The Invoker is associated with one or several commands and sends requests
    to them.
    """
    _on_start: Optional[Command] = None
    _on_finish: Optional[Command] = None
    _history: List[Command] = []
    _undo_stack: List[Command] = []
    
    def set_on_start(self, command: Command) -> None:
        """
        Set the command to be executed at the start.
        
        Args:
            command: The command to execute at the start.
        """
        self._on_start = command
    
    def set_on_finish(self, command: Command) -> None:
        """
        Set the command to be executed at the end.
        
        Args:
            command: The command to execute at the end.
        """
        self._on_finish = command
    
    def execute_command(self, command: Command) -> None:
        """
        Execute a command and add it to the history.
        
        Args:
            command: The command to execute.
        """
        self._history.append(command)
        command.execute()
    
    def execute_with_undo(self, command: Command) -> None:
        """
        Execute a command and push it onto the undo stack.
        
        Args:
            command: The command to execute.
        """
        command.execute()
        self._undo_stack.append(command)
    
    def undo(self) -> None:
        """
        Undo the most recent command from the undo stack.
        """
        if not self._undo_stack:
            print("Nothing to undo")
            return
        
        command = self._undo_stack.pop()
        command.undo()
    
    def run(self) -> None:
        """
        Run the invoker, executing the start and finish commands if they exist.
        """
        print("Invoker: Starting...")
        if self._on_start:
            self._on_start.execute()
        
        print("Invoker: ...doing something really important...")
        
        print("Invoker: Finishing...")
        if self._on_finish:
            self._on_finish.execute()

class FileOperationCommand(Command):
    """
    A concrete command that performs file operations with undo support.
    """
    def __init__(self, filename: str, content: str) -> None:
        """
        Initialize with filename and content.
        
        Args:
            filename: The name of the file to operate on.
            content: The content to write to the file.
        """
        self._filename = filename
        self._content = content
        self._backup: Optional[str] = None
    
    def execute(self) -> None:
        """
        Execute the file write operation.
        """
        # Backup existing content if file exists
        if os.path.exists(self._filename):
            with open(self._filename, 'r') as file:
                self._backup = file.read()
        
        # Write new content
        with open(self._filename, 'w') as file:
            file.write(self._content)
    
    def undo(self) -> None:
        """
        Undo the file write operation by restoring the backup.
        """
        if self._backup is not None:
            with open(self._filename, 'w') as file:
                file.write(self._backup)
        elif os.path.exists(self._filename):
            os.remove(self._filename)

class MacroCommand(Command):
    """
    A command that executes a list of commands.
    """
    def __init__(self, commands: List[Command]) -> None:
        """
        Initialize with a list of commands.
        
        Args:
            commands: A list of commands to execute.
        """
        self._commands = commands
    
    def execute(self) -> None:
        """
        Execute all commands in sequence.
        """
        for command in self._commands:
            command.execute()
    
    def undo(self) -> None:
        """
        Undo all commands in reverse order.
        """
        for command in reversed(self._commands):
            command.undo()

# ============================================
# Transaction Support
# ============================================

class Transaction:
    """
    A transaction that can contain multiple commands and be committed or rolled back.
    """
    def __init__(self) -> None:
        """Initialize a new transaction."""
        self._commands: List[Command] = []
        self._completed = False
    
    def add_command(self, command: Command) -> None:
        """
        Add a command to the transaction.
        
        Args:
            command: The command to add.
        """
        if self._completed:
            raise RuntimeError("Cannot add commands to a completed transaction")
        self._commands.append(command)
    
    def commit(self) -> None:
        """
        Execute all commands in the transaction.
        """
        if self._completed:
            raise RuntimeError("Transaction already completed")
        
        try:
            for command in self._commands:
                command.execute()
            self._completed = True
        except Exception as e:
            self.rollback()
            raise
    
    def rollback(self) -> None:
        """
        Undo all commands in reverse order.
        """
        for command in reversed(self._commands):
            try:
                command.undo()
            except Exception as e:
                # Log the error but continue undoing other commands
                print(f"Error during rollback: {e}")
        self._completed = True

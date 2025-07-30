"""
Factory Pattern implementations.

This module provides implementations of the Factory design pattern,
which provides an interface for creating objects in a superclass,
but allows subclasses to alter the type of objects that will be created.
"""
from enum import Enum, auto
from typing import TypeVar, Type, Dict, Any, Optional, Protocol, runtime_checkable

T = TypeVar('T')

class AnimalType(Enum):
    """Enumeration of animal types for the AnimalFactory."""
    DOG = auto()
    CAT = auto()
    BIRD = auto()

class Animal:
    """Base class for all animals."""
    def __init__(self, name: str):
        self.name = name
    
    def speak(self) -> str:
        """Return the sound the animal makes."""
        raise NotImplementedError
    
    def make_sound(self) -> str:
        """Alias for speak method."""
        return self.speak()

class Dog(Animal):
    """A dog animal implementation."""
    def speak(self) -> str:
        return "Woof!"

class Cat(Animal):
    """A cat animal implementation."""
    def speak(self) -> str:
        return "Meow!"

class Bird(Animal):
    """A bird animal implementation."""
    def speak(self) -> str:
        return "Chirp!"

class AnimalFactory:
    """Factory for creating different types of animals."""
    _animal_classes = {
        AnimalType.DOG: Dog,
        AnimalType.CAT: Cat,
        AnimalType.BIRD: Bird
    }
    
    @classmethod
    def create_animal(cls, animal_type: AnimalType, name: str = "Animal") -> Animal:
        """
        Create an animal of the specified type.
        
        Args:
            animal_type: The type of animal to create
            name: The name of the animal (defaults to "Animal")
            
        Returns:
            An instance of the specified animal type
            
        Raises:
            ValueError: If the animal type is not supported
        """
        if animal_type not in cls._animal_classes:
            raise ValueError(f"Unsupported animal type: {animal_type}")
            
        return cls._animal_classes[animal_type](name)

@runtime_checkable
class Factory(Protocol[T]):
    """Protocol defining the factory interface."""
    def create(self, *args: Any, **kwargs: Any) -> T:
        """Create and return a new instance."""
        ...

class SimpleFactory(Factory[T]):
    """
    A simple factory that creates instances of a given class.
    
    Args:
        cls: The class to instantiate
    """
    def __init__(self, cls: Type[T]):
        self._cls = cls
    
    def create(self, *args: Any, **kwargs: Any) -> T:
        """Create and return a new instance of the configured class."""
        return self._cls(*args, **kwargs)

class ClassFactory(Factory[T]):
    """
    A factory that creates instances based on a class name or key.
    
    Args:
        class_map: Dictionary mapping keys to classes
        default_class: Default class to use if key not found (optional)
    """
    def __init__(self, class_map: Dict[str, Type[T]], default_class: Optional[Type[T]] = None):
        self._class_map = class_map
        self._default_class = default_class
    
    def create(self, key: str, *args: Any, **kwargs: Any) -> T:
        """
        Create and return a new instance based on the key.
        
        Args:
            key: The key to look up the class
            *args: Positional arguments to pass to the constructor
            **kwargs: Keyword arguments to pass to the constructor
            
        Returns:
            A new instance of the requested class
            
        Raises:
            KeyError: If the key is not found and no default class is set
        """
        cls = self._class_map.get(key, self._default_class)
        if cls is None:
            raise KeyError(f"No class found for key '{key}' and no default class set")
        return cls(*args, **kwargs)

# Example usage
if __name__ == "__main__":
    from dataclasses import dataclass
    
    @dataclass
    class Button:
        label: str
        
        def click(self) -> str:
            return f"{self.label} button clicked"
    
    # SimpleFactory example
    button_factory = SimpleFactory(Button)
    ok_button = button_factory.create(label="OK")
    print(ok_button.click())  # Output: OK button clicked
    
    # ClassFactory example
    class WindowsButton(Button):
        def click(self) -> str:
            return f"Windows style: {super().click()}"
    
    class MacButton(Button):
        def click(self) -> str:
            return f"Mac style: {super().click()}"
    
    button_factory = ClassFactory({
        "windows": WindowsButton,
        "mac": MacButton
    }, default_class=Button)
    
    win_button = button_factory.create("windows", label="Submit")
    print(win_button.click())  # Output: Windows style: Submit button clicked
    
    default_button = button_factory.create("linux", label="Cancel")
    print(default_button.click())  # Output: Cancel button clicked

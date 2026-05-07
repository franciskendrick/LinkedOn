from abc import ABC, abstractmethod


class Entity(ABC):
    @abstractmethod
    def display(self):
        """Print a formatted view of the entity to the terminal."""
        pass

    @abstractmethod
    def to_dict(self):
        """Serialize the entity to a dictionary for JSON storage."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        """Deserialize and reconstruct the entity from a dictionary."""
        pass

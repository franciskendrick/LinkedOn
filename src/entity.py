from abc import ABC, abstractmethod


class Entity(ABC):
    # Print a formatted view of the entity to the terminal
    @abstractmethod
    def display(self):
        pass

    # Serialize the entity to a dictionary for JSON storage
    @abstractmethod
    def to_dict(self):
        pass

    # Deserialize and reconstruct the entity from a dictionary
    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        pass

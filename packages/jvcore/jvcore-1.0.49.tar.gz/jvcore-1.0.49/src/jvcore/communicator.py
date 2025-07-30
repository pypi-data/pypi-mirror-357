from abc import ABC, abstractmethod
from .singleton import Singleton

class Communicator(ABC, metaclass=Singleton):    
    @abstractmethod
    def say(self, text: str):
        pass
    
    @abstractmethod
    def sayAndPrint(self, text: str):
        pass
    
    @abstractmethod
    def print(self, text: str):
        pass
    
    @abstractmethod
    def getTextInput(self, question: str) -> str:
        pass

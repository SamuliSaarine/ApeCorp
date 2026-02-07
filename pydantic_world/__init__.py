from .utils.get_model import get_model
from .utils.load_md import load_md
from abc import abstractmethod, ABC

class Entity(ABC):
    @abstractmethod
    def view(self) -> str:
        pass
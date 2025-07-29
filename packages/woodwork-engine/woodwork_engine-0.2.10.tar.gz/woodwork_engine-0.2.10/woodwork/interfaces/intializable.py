from abc import ABC, abstractmethod


class Initializable(ABC):
    @abstractmethod
    def init(self, config: dict):
        pass

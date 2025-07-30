import re
from abc import ABC, abstractmethod


class RuleFunction(ABC):
    name = None

    @staticmethod
    def _snakify_name(name):
        pattern = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
        name = pattern.sub("_", name).lower()
        return name

    def __init__(self):
        if self.name is None:
            self.name = self._snakify_name(self.__class__.__name__)

    @abstractmethod
    def run(self, *args, **kwargs) -> bool:
        raise NotImplementedError("Method must be implemented in subclass.")

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

import abc


class AbstractNotifier(abc.ABC):
    @abc.abstractmethod
    def send(self, target, message: str, payload: dict | None) -> bool:
        pass

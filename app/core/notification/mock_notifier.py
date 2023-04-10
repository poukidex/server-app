import logging

from core.notification.abstract_notifier import AbstractNotifier

logger = logging.getLogger(f"ctaive.{__name__}")


class MockNotifier(AbstractNotifier):
    def send(self, target, message: str, payload: dict | None) -> bool:
        logger.info(f"Mocking message to {target}: {message}")
        return True

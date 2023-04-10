import logging

from push_notifications.models import GCMDevice

from core.notification.abstract_notifier import AbstractNotifier

logger = logging.getLogger(f"ctaive.{__name__}")


class Notifier(AbstractNotifier):
    def send(self, target, message: str, payload: dict | None) -> bool:
        logger.info(f"message to {target}: {message}")

        try:
            fcm_device = GCMDevice.objects.get(user=target)
        except GCMDevice.DoesNotExist:
            logger.error(f"Could not find device registered for user {target}")
            return False

        try:
            fcm_device.send_message(message, extra=payload)
        except Exception:
            logger.exception("Could not send message")
            return False

        return True

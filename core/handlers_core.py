# core/handlers_core.py
#
# Обработчики входящих вебхуков IronRelay.

from core.tasks import task


@task
def handle_incoming_webhook(event, payload):
    """
    Тестовый обработчик входящих вебхуков.

    Пока просто печатает событие и данные.
    Потом сюда можно навесить любую бизнес-логику:
    создание пользователей, оплат, уведомлений и т.д.
    """
    print("=== HANDLE WEBHOOK ===")
    print("Event:", event)
    print("Payload:", payload)

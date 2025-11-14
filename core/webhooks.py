import json
import urllib.request
import urllib.error

from django.utils import timezone

from .models import IronWebhookDelivery
from .tasks import task


@task
def _perform_webhook_delivery(delivery_id):
    """
    Внутренняя задача: отправляет один вебхук по HTTP.
    Вызывается воркером через очередь IronTask.
    """
    delivery = IronWebhookDelivery.objects.get(id=delivery_id)

    # отмечаем ещё одну попытку
    delivery.attempts += 1

    data = json.dumps(delivery.payload).encode("utf-8")

    req = urllib.request.Request(
        delivery.target_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "IronRelayWebhook/1.0",
            "X-IronRelay-Event": delivery.event,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            delivery.last_response_code = resp.status
            delivery.last_response_body = body[:2000]  # режем чтобы не раздувать БД
            delivery.status = IronWebhookDelivery.STATUS_SUCCESS
            delivery.last_error = ""
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        delivery.last_response_code = e.code
        delivery.last_response_body = body[:2000]
        delivery.status = IronWebhookDelivery.STATUS_FAILED
        delivery.last_error = f"HTTPError: {e}"
        raise  # даём задаче упасть, чтобы сработали ретраи IronTask
    except Exception as e:
        delivery.last_error = str(e)
        delivery.status = IronWebhookDelivery.STATUS_FAILED
        raise
    finally:
        delivery.updated_at = timezone.now()
        delivery.save()


def send_webhook(event: str, target_url: str, payload: dict, max_attempts: int = 5):
    """
    Публичная функция: создаёт запись вебхука и ставит его в очередь.
    Её будет вызывать разработчик в своём проекте.
    """
    delivery = IronWebhookDelivery.objects.create(
        event=event,
        target_url=target_url,
        payload=payload,
        status=IronWebhookDelivery.STATUS_PENDING,
        max_attempts=max_attempts,
        attempts=0,
    )

    # ставим задачу в очередь: отправить этот вебхук
    _perform_webhook_delivery.defer(str(delivery.id), max_attempts=max_attempts)
    return delivery

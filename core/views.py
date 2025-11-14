# core/views.py
#
# Представления для IronRelay:
# - дашборд
# - входящие вебхуки
# - JSON-статус

import json
import django

from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from core.models import (
    IronTask,
    IronWebhookDelivery,
    IronIncomingWebhook,
)
from core.handlers_core import handle_incoming_webhook



def ironrelay_dashboard(request: HttpRequest) -> HttpResponse:
    """
    Красивый дашборд IronRelay.

    URL: /ironrelay/
    Показывает:
      - последние задачи
      - исходящие вебхуки
      - входящие вебхуки
      - общую статистику для карточек
    """
    recent_tasks = IronTask.objects.order_by("-created_at")[:10]
    outgoing_webhooks = IronWebhookDelivery.objects.order_by("-created_at")[:10]
    incoming_webhooks = IronIncomingWebhook.objects.order_by("-created_at")[:10]

    stats = {
        "pending_tasks": IronTask.objects.filter(
            status=IronTask.STATUS_PENDING
        ).count(),
        "running_tasks": IronTask.objects.filter(
            status=IronTask.STATUS_RUNNING
        ).count(),
        "failed_tasks": IronTask.objects.filter(
            status=IronTask.STATUS_FAILED
        ).count(),
        "success_webhooks": IronWebhookDelivery.objects.filter(
            status=IronWebhookDelivery.STATUS_SUCCESS
        ).count(),
    }

    context = {
        "recent_tasks": recent_tasks,
        "outgoing_webhooks": outgoing_webhooks,
        "incoming_webhooks": incoming_webhooks,
        "stats": stats,
    }
    return render(request, "core/dashboard.html", context)


@csrf_exempt
def ironrelay_incoming(request: HttpRequest, source: str) -> JsonResponse:
    """
    Универсальный endpoint для входящих вебхуков.

    URL: /ironrelay/incoming/<source>/

    Пример:
      POST /ironrelay/incoming/stripe/
      Body:
        {
          "event": "invoice.paid",
          "user_id": 123,
          "data": {...}
        }
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        raw_body = request.body.decode("utf-8") or "{}"
        data = json.loads(raw_body)
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    event = data.get("event", "") or ""

    # сохраняем входящий вебхук
    webhook = IronIncomingWebhook.objects.create(
        source=source,
        event=event,
        payload=data,
    )

    # ставим задачу на обработку в очередь IronRelay
    handle_incoming_webhook.defer(event, data)

    return JsonResponse(
        {
            "id": str(webhook.id),
            "status": "received",
        },
        status=201,
    )


def ironrelay_status(request: HttpRequest) -> JsonResponse:
    """
    JSON-статус IronRelay для health-check.

    URL: /ironrelay/status/

    Возвращает:
      - время
      - версию Django
      - статистику задач и вебхуков
    """
    stats = {
        "pending_tasks": IronTask.objects.filter(
            status=IronTask.STATUS_PENDING
        ).count(),
        "running_tasks": IronTask.objects.filter(
            status=IronTask.STATUS_RUNNING
        ).count(),
        "failed_tasks": IronTask.objects.filter(
            status=IronTask.STATUS_FAILED
        ).count(),
        "success_webhooks": IronWebhookDelivery.objects.filter(
            status=IronWebhookDelivery.STATUS_SUCCESS
        ).count(),
        "total_incoming": IronIncomingWebhook.objects.count(),
        "total_tasks": IronTask.objects.count(),
        "total_deliveries": IronWebhookDelivery.objects.count(),
    }

    return JsonResponse(
        {
            "ok": True,
            "timestamp": timezone.now().isoformat(),
            "django_version": django.get_version(),
            "app": "ironrelay",
            "stats": stats,
        }
    )
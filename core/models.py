import uuid
from django.db import models
from django.utils import timezone


class IronTask(models.Model):
    """
    Фоновые задачи IronRelay.

    Хранит, что за функцию надо выполнить, с какими аргументами
    и в каком состоянии она сейчас находится.
    """

    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Полное имя функции задачи, например: "app.tasks.send_welcome_email"
    name = models.CharField(max_length=255)

    # Аргументы задачи: {"args": [...], "kwargs": {...}}
    payload = models.JSONField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )

    # Приоритет: чем больше число, тем "важнее"
    priority = models.IntegerField(default=0, db_index=True)

    # Когда задачу можно забирать в работу
    scheduled_at = models.DateTimeField(default=timezone.now, db_index=True)

    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=5)

    last_error = models.TextField(blank=True)

    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "iron_task"
        ordering = ["-priority", "scheduled_at"]
        indexes = [
            models.Index(fields=["status", "scheduled_at"]),
            models.Index(fields=["status", "priority"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} [{self.status}]"


class IronWebhookDelivery(models.Model):
    """
    Исходящие вебхуки, которые IronRelay отправляет по HTTP.
    """

    STATUS_PENDING = "pending"
    STATUS_SENDING = "sending"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SENDING, "Sending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    event = models.CharField(max_length=255, db_index=True)
    target_url = models.URLField()

    payload = models.JSONField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )

    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=5)

    last_response_code = models.IntegerField(null=True, blank=True)
    last_response_body = models.TextField(blank=True)
    last_error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "iron_webhook_delivery"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.event} -> {self.target_url} [{self.status}]"


class IronIncomingWebhook(models.Model):
    """
    Лог входящих вебхуков, которые пришли к нашему сайту.
    """

    STATUS_RECEIVED = "received"
    STATUS_HANDLED = "handled"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_RECEIVED, "Received"),
        (STATUS_HANDLED, "Handled"),
        (STATUS_FAILED, "Failed"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    source = models.CharField(
        max_length=100,
        help_text="Например: stripe, github, custom",
    )

    event = models.CharField(max_length=255, blank=True)

    payload = models.JSONField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_RECEIVED,
        db_index=True,
    )

    # Сюда потом можно будет привязать задачу обработки
    handler_task = models.ForeignKey(
        IronTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incoming_webhooks",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "iron_incoming_webhook"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["source", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.source} [{self.event or 'no event'}]"

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import IronTask, IronIncomingWebhook, IronWebhookDelivery


class StatusColorMixin:
    """
    иксин для красивого отображения статуса цветным бейджем.
    """

    STATUS_COLORS = {
        "pending": "#facc15",   # жёлтый
        "running": "#38bdf8",   # голубой
        "failed": "#f97373",    # красный
        "success": "#22c55e",   # зелёный
        "sending": "#38bdf8",
        "received": "#38bdf8",
    }

    def render_status_badge(self, value: str) -> str:
        color = self.STATUS_COLORS.get(value, "#e5e7eb")
        return format_html(
            '<span style="display:inline-block; padding:2px 8px; '
            "border-radius:999px; font-size:11px; font-weight:600; "
            "background:{bg}; color:#020617; text-transform:uppercase;"
            '">{text}</span>',
            bg=color,
            text=value,
        )


@admin.register(IronTask)
class IronTaskAdmin(StatusColorMixin, admin.ModelAdmin):
    """
    адачи очереди.
    """

    list_display = (
        "short_id",
        "name",
        "status_colored",
        "priority",
        "attempts",
        "scheduled_at",
        "created_at",
    )
    list_filter = ("status", "priority", "created_at")
    search_fields = ("id", "name")
    ordering = ("-created_at",)

    readonly_fields = (
        "id",
        "name",
        "status",
        "payload",
        "priority",
        "attempts",
        "scheduled_at",
        "created_at",
        "updated_at",
        "last_error",
    )

    actions = ["retry_failed_tasks"]

    def short_id(self, obj):
        return str(obj.id)[:8]

    short_id.short_description = "ID"

    def status_colored(self, obj):
        return self.render_status_badge(obj.status)

    status_colored.short_description = "Status"
    status_colored.admin_order_field = "status"

    @admin.action(description="овторно запустить (Retry) только FAILED задачи")
    def retry_failed_tasks(self, request, queryset):
        """
        ерезапускает только те задачи, у которых статус FAILED.
        """
        from .models import IronTask as IronTaskModel

        restarted = 0
        for task in queryset:
            if task.status == IronTaskModel.STATUS_FAILED:
                task.status = IronTaskModel.STATUS_PENDING
                task.attempts = 0
                task.scheduled_at = timezone.now()
                task.last_error = ""
                task.save(
                    update_fields=[
                        "status",
                        "attempts",
                        "scheduled_at",
                        "last_error",
                    ]
                )
                restarted += 1

        self.message_user(request, f"ерезапущено задач: {restarted}")


@admin.register(IronIncomingWebhook)
class IronIncomingWebhookAdmin(StatusColorMixin, admin.ModelAdmin):
    """
    ходящие вебхуки.
    """

    list_display = (
        "short_id",
        "source",
        "event",
        "status_colored",
        "created_at",
    )
    list_filter = ("status", "source", "created_at")
    search_fields = ("id", "source", "event")
    ordering = ("-created_at",)

    readonly_fields = (
        "id",
        "source",
        "event",
        "status",
        "payload",
        "created_at",
    )

    def short_id(self, obj):
        return str(obj.id)[:8]

    short_id.short_description = "ID"

    def status_colored(self, obj):
        return self.render_status_badge(obj.status)

    status_colored.short_description = "Status"
    status_colored.admin_order_field = "status"


@admin.register(IronWebhookDelivery)
class IronWebhookDeliveryAdmin(StatusColorMixin, admin.ModelAdmin):
    """
    сходящие вебхуки (доставки).
    """

    list_display = (
        "short_id",
        "event",
        "status_colored",
        "last_response_code",
        "attempts",
        "created_at",
    )
    list_filter = ("status", "last_response_code", "created_at")
    search_fields = ("id", "event", "target_url")
    ordering = ("-created_at",)

    readonly_fields = (
        "id",
        "event",
        "target_url",
        "status",
        "payload",
        "attempts",
        "last_response_code",
        "last_response_body",
        "created_at",
    )

    def short_id(self, obj):
        return str(obj.id)[:8]

    short_id.short_description = "ID"

    def status_colored(self, obj):
        return self.render_status_badge(obj.status)

    status_colored.short_description = "Status"
    status_colored.admin_order_field = "status"

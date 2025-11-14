import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from core.models import IronTask
from core.tasks import IronTaskWrapper


class Command(BaseCommand):
    help = "IronRelay worker – выполняет фоновые задачи"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("IronRelay worker started"))

        while True:
            now = timezone.now()

            task = (
                IronTask.objects
                .filter(
                    status=IronTask.STATUS_PENDING,
                    scheduled_at__lte=now
                )
                .order_by("-priority", "scheduled_at")
                .first()
            )

            if not task:
                time.sleep(1)
                continue

            # Лочим задачу
            with transaction.atomic():
                task = IronTask.objects.select_for_update().get(id=task.id)
                if task.status != IronTask.STATUS_PENDING:
                    continue

                task.status = IronTask.STATUS_RUNNING
                task.locked_at = now
                task.locked_by = "local-worker"
                task.save()

            self.stdout.write(f"Running task {task.id} ({task.name})")

            try:
                IronTaskWrapper.run_task(task)
                task.status = IronTask.STATUS_SUCCESS
                task.save()
                self.stdout.write(self.style.SUCCESS(f"Task {task.id} done"))

            except Exception as e:
                task.attempts += 1
                task.last_error = str(e)

                if task.attempts >= task.max_attempts:
                    task.status = IronTask.STATUS_FAILED
                    self.stdout.write(self.style.ERROR(f"Task {task.id} FAILED"))

                else:
                    # retry через 3 сек
                    task.scheduled_at = timezone.now() + timezone.timedelta(seconds=3)
                    task.status = IronTask.STATUS_PENDING
                    self.stdout.write(self.style.WARNING(f"Retry task {task.id}"))

                task.save()

            time.sleep(0.2)

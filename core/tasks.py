import importlib
from functools import wraps

from django.db import transaction
from django.utils import timezone

from .models import IronTask


def _import_string(path: str):
    """
    Импортирует функцию по строковому пути:
    "app.tasks.send_email" -> function
    """
    module_name, func_name = path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, func_name)


class IronTaskWrapper:
    """
    Обёртка над функцией, которую помечаем @task.
    """

    def __init__(self, func):
        self.func = func
        self.name = f"{func.__module__}.{func.__name__}"

    def __call__(self, *args, **kwargs):
        # обычный вызов функции — если кто-то вызовет напрямую
        return self.func(*args, **kwargs)

    def defer(self, *args, delay: int = 0, priority: int = 0, max_attempts=5, **kwargs):
        """
        Создаёт запись задачи в БД (но только после успешного commit-а).
        """
        payload = {
            "args": args,
            "kwargs": kwargs,
        }

        def _create():
            IronTask.objects.create(
                name=self.name,
                payload=payload,
                priority=priority,
                max_attempts=max_attempts,
                scheduled_at=timezone.now() + timezone.timedelta(seconds=delay),
            )

        # Важный момент: задача создаётся только ПОСЛЕ commit
        transaction.on_commit(_create)

    @staticmethod
    def run_task(task: IronTask):
        """
        Выполняет задачу (используется воркером).
        """
        func = _import_string(task.name)
        args = task.payload.get("args", [])
        kwargs = task.payload.get("kwargs", {})
        return func(*args, **kwargs)


def task(func):
    """
    Декоратор: превращает любую функцию в задачу IronRelay.
    """
    wrapper = IronTaskWrapper(func)

    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    inner.defer = wrapper.defer
    inner._iron_task = wrapper

    return inner


@task
def test_print(message):
    print("TASK SAYS:", message)

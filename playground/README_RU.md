# IronRelay от Syden  
Лёгкая очередь задач и вебхуков для Django.  
Автор: **Denys Sykhov (Syden)**

## Возможности
- Приём входящих вебхуков
- Отправка исходящих вебхуков (POST)
- Повторные попытки при ошибках
- Очередь задач без Celery и Redis
- Удобная админ‑панель
- MIT лицензия — можно продавать

## Установка
```
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Запуск worker
```
python manage.py ironrelay_worker
```

## Входящие вебхуки
POST /ironrelay/incoming/<source>/
```
{
  "event": "ping",
  "user_id": 1
}
```

## Исходящие вебхуки
```
from core.tasks import send_webhook
send_webhook.defer("test.event", {"hello":"world"}, "https://example.com")
```

## Статус
GET /ironrelay/status/
Возвращает JSON со статистикой.

## Лицензия
MIT — разрешено коммерческое использование.

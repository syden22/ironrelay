# IronRelay by Syden  
Lightweight queue & webhook engine for any Django project.  
Author: **Denys Sykhov (Syden)**

## Features
- Incoming webhooks processing
- Outgoing webhooks with retry & logging
- Task queue on pure Django ORM (no Celery, no Redis)
- Dashboard
- MIT license — commercial use allowed

## Installation
```
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Worker
```
python manage.py ironrelay_worker
```

## Incoming Webhooks
POST /ironrelay/incoming/<source>/
```
{
  "event": "ping",
  "user_id": 1
}
```

## Outgoing Webhooks
```
from core.tasks import send_webhook
send_webhook.defer("test.event", {"hello":"world"}, "https://example.com")
```

## Status
GET /ironrelay/status/
Returns JSON with statistics.

## License
MIT — free for commercial use.

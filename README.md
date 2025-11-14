# ironrelay
Lightweight task queue and webhook dashboard for Django (no Redis, no Celery)
# IronRelay – Simple Task Queue & Webhook Dashboard for Django

**IronRelay** is a lightweight task queue and webhook manager for Django projects.  
No Redis, no Celery – everything runs on plain Django ORM with a simple worker and a small dashboard.

Perfect for small/medium projects, APIs, and side-projects where Celery would be overkill.

---

## Features

- ✅ Background tasks stored in the database (`IronTask`)
- ✅ Simple decorator API: `@task` + `.defer(...)`
- ✅ Worker process: `python manage.py ironrelay_worker`
- ✅ Outgoing webhooks with delivery logs (`IronWebhookDelivery`)
- ✅ Incoming webhook log (`IronIncomingWebhook`)
- ✅ Minimal dashboard to inspect tasks & webhooks
- ✅ Small playground project included

---

## Installation

1. Install dependencies (Django >= 4.2 and requests):

```bash
pip install -r requirements.txt
# or make sure you have:
# django>=4.2
# requests
Add the app to INSTALLED_APPS in your settings.py:

INSTALLED_APPS = [
    # ...
    "core",  # IronRelay app
]


Apply migrations:

python manage.py migrate


(Optional) Add URLs for the dashboard and incoming webhooks:

from django.urls import path
from core import views

urlpatterns = [
    # ...
    path("ironrelay/", views.ironrelay_dashboard, name="ironrelay_dashboard"),
    path("ironrelay/status/", views.ironrelay_status_json, name="ironrelay_status_json"),
    path(
        "ironrelay/incoming/<str:source>/",
        views.ironrelay_incoming_webhook,
        name="ironrelay_incoming",
    ),
]

Usage
1) Define a task
# myapp/tasks.py
from core.tasks import task

@task
def send_welcome_email(user_id: int):
    # your logic here
    ...

2) Defer a task
# e.g. in a Django view
from myapp.tasks import send_welcome_email

def signup_view(request):
    # create user ...
    send_welcome_email.defer(user.id)
    ...

3) Run the worker
python manage.py ironrelay_worker


Keep this process running (separate terminal, systemd service, etc.).
It will pick up pending tasks, execute them, and update the status in the database.

Webhooks
Outgoing webhooks

Use helper functions from core.webhooks to send outgoing webhooks and log every delivery
(status code, response body, errors, retries, etc.) as IronWebhookDelivery records.

Incoming webhooks

POST any JSON payload to:

/ironrelay/incoming/<source>/


The payload will be stored as IronIncomingWebhook and visible in the dashboard.

Playground project

This repository includes a small playground Django project (playground) so you can:

run the example project,

open the dashboard,

play with tasks and webhooks before integrating IronRelay into your own code.

License

MIT – use it for commercial or personal projects.
If you find it useful, a star on GitHub or feedback is appreciated 🙂

Pro version on Gumroad

If you want a more polished version with extra features and examples,
you can support development and get the Pro build here:

👉 https://syxov.gumroad.com/l/hkobs

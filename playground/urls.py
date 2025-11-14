
# playground/urls.py

from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from core.views import (
    ironrelay_incoming,
    ironrelay_dashboard,
    ironrelay_status,
)

urlpatterns = [
    # 🔹 Корень сайта -> редирект на дашборд IronRelay
    path(
        "",
        RedirectView.as_view(
            pattern_name="ironrelay_dashboard",
            permanent=False,
        ),
        name="home_redirect",
    ),

    # 🔹 Админка Django
    path("admin/", admin.site.urls),

    # 🔹 Входящие вебхуки
    path(
        "ironrelay/incoming/<str:source>/",
        ironrelay_incoming,
        name="ironrelay_incoming",
    ),

    # 🔹 Дашборд IronRelay
    path(
        "ironrelay/",
        ironrelay_dashboard,
        name="ironrelay_dashboard",
    ),

    # 🔹 Статус API
    path(
        "ironrelay/status/",
        ironrelay_status,
        name="ironrelay_status",
    ),
]

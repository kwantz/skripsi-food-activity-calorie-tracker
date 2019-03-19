from django.urls import path
from . import views

urlpatterns = [
    path('migrate/', views.migrate_init, name = "migrate_init"),
    path('tracking/', views.tracking_view, name = "tracking_view")
]
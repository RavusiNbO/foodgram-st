from django.urls import path
from .views import link_handler

urlpatterns = [
    path('recipes/<int:pk>/get-link/', link_handler, name='get-link'),
]
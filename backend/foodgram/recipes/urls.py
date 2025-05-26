from django.urls import path
from .views import link_handler

urlpatterns = [
    path('<int:pk>/', link_handler, name='link_handler'),
]
from django.urls import path, include
from api.urls import router

urlpatterns = [
    path('', include(router.urls)),
]
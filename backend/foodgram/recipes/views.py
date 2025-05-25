from rest_framework.decorators import api_view
from django.shortcuts import redirect, get_object_or_404
from .models import Recipe


@api_view(["get",])
def link_handler(request, pk):
    get_object_or_404(Recipe, pk=pk)
    return redirect("api:recipes", pk=pk)

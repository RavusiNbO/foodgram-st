from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET"])
def get_short_link(request, pk=None):
    res = request.build_absolute_uri().split("get-link")[0]
    return Response({
        "short-link": res,
    }, status=status.HTTP_200_OK)

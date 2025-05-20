from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageLimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 6
    max_page_size = 100


from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageLimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })
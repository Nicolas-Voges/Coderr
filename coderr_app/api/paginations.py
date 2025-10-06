"""
Defines custom pagination settings for the Coderr app.
"""

from rest_framework.pagination import PageNumberPagination

class ResultsSetPagination(PageNumberPagination):
    """ Custom pagination class for API results."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Класс, переопределяющий пагинацию для представлений API"""
    page_size_query_param = "limit"
    max_page_size = 15
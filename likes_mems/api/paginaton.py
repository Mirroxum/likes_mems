from rest_framework import pagination

from likes_mems.conf import DASBOARD_PAGINATION


class DashboardPagination(pagination.PageNumberPagination):
    page_size = DASBOARD_PAGINATION

import math
from collections import OrderedDict
from typing import Optional

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):

    def get_next_link(self) -> Optional[int]:
        """Returns only number of next page."""
        if not self.page.has_next():
            return None
        return self.page.next_page_number()

    def get_previous_link(self) -> Optional[int]:
        """Returns only number of previous page."""
        if not self.page.has_previous():
            return None
        return self.page.previous_page_number()

    def get_paginated_response(self, data: list) -> Response:
        """
        Returns paginated response.

        Includes:
            - count of pages (not records count);
            - next page number;
            - previous page number;
            - paginated results.
        """
        return Response(OrderedDict([
            ('count', math.ceil(self.page.paginator.count / self.page_size)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

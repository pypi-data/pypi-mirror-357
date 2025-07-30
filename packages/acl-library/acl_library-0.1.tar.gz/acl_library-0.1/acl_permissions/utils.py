from uuid import uuid4
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.response import Response

class ResponseInfo:
    def __init__(self, *, status=True, status_code=200, message='', data=None, errors=None):
        self.response = {
            "status": status,
            "status_code": status_code,
            "message": message,
            "data": data if data is not None else {},
            "errors": errors if errors is not None else {},
        }


from rest_framework.response import Response

class APIUtils:
    @classmethod
    def handle_error_response(cls, errors="", status_code=400, message=""):
        # Normalize error message to string
        error_message = str(errors).lower()

        # Check if it's an invalid page error
        if "invalid page" in error_message or "page" in error_message:
            return Response({
                "status_code": 200,
                "message": "No data available",
                "errors": {},
                "data": [],
                "status": True
            }, status=200)

        # Default error response
        response_format = {
            "status_code": status_code,
            "message": message,
            "errors": errors,
            "status": False
        }
        return Response(response_format, status=status_code)

class RestPagination(PageNumberPagination):
    
    page_size = 25
    page_size_query_param = 'limit'
    
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(RestPagination, self).__init__(**kwargs)

    def get_paginated_response(self, data):
        data = {
            'links': {
                'next': "" if self.get_next_link() is None else self.get_next_link().split('/api')[1],
                'previous': "" if self.get_previous_link() is None else self.get_previous_link().split('/api')[1]
            },
            'count': len(self.page),
            'total_count': self.page.paginator.count,
            'current_page': self.page.number,
            'next_page': self.page.next_page_number() if self.page.has_next() else None,
            'previous_page': self.page.previous_page_number() if self.page.has_previous() else None,
            'results': data
        }
        
        self.response_format['status_code'] = status.HTTP_200_OK
        self.response_format["data"] = data
        self.response_format["status"] = True
        
        return Response(self.response_format, status=status.HTTP_200_OK)

from typing import Dict, Any, Optional, List, Union
from rest_framework.response import Response
from rest_framework import status as drf_status

class ResponseMixin:

    """
    Mixin to provide a standard response format for API endpoints.
    This mixin can be used in Django REST Framework views to ensure
    consistent response structure across the application.
    """

    def response(
        self, 
        data: Any = None, 
        message: str = "", 
        error: Union[Dict, List, str, None] = None,
        status_code: int = drf_status.HTTP_200_OK, 
        status=None,
        count=None,
        next=None,
        previous=None
    ) -> Response:
        """
        Standard response format for API endpoints
        
        Args:
            data: The data to return in the response
            message: A human-readable message about the response
            error: Error details if applicable
            status_code: HTTP status code
            
        Returns:
            A DRF Response object with standardized structure
        """
        response_data = {
            "status": "success" if not error else "error",
        }
        
        if message:
            response_data["message"] = message
            
        if data is not None:
            response_data["data"] = data
            
        if error is not None:
            response_data['error'] = error
            
        if count is not None:
            response_data["count"] = count
        if next is not None:
            response_data["next"] = next
        if previous is not None:
            response_data["previous"] = previous
            
        return Response(data=response_data, status=status or status_code)

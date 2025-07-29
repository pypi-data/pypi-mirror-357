"""
Core response classes for standardizing DRF API responses.

This module provides the foundation for creating consistent API responses
across your Django REST Framework project.
"""
from typing import Any, Dict, Optional

from rest_framework import status
from rest_framework.response import Response


class StandardResponse:
    """
    Standard API response structure for consistent API communication.

    This class provides static methods to generate standardized success and error responses
    for API endpoints, ensuring a consistent response format throughout your API.

    Standard success response format:
    {
        "success": true,
        "message": "Success message",
        "data": { ... response data ... },
        "meta": { ... optional metadata ... }
    }

    Standard error response format:
    {
        "success": false,
        "message": "Error message",
        "errors": { ... optional error details ... }
    }
    """

    @staticmethod
    def success(
            data: Any = None,
            message: str = "Success",
            status_code: int = status.HTTP_200_OK,
            meta: Optional[Dict] = None
    ) -> Response:
        """
        Generate a standardized success response.

        Args:
            data (Any): The data to include in the response body.
            message (str): A success message (default: "Success").
            status_code (int): HTTP status code for the response (default: 200 OK).
            meta (Optional[Dict]): Additional metadata to include in the response.

        Returns:
            Response: A DRF Response object with the standardized success structure.
        """
        response = {
            "success": True,  # Indicates the request was successful
            "message": message,  # Success message
            "data": data,  # Data payload
        }

        if meta:
            response["meta"] = meta  # Add metadata if provided

        return Response(response, status=status_code)

    @staticmethod
    def error(
            message: str = "An error occurred",
            status_code: int = status.HTTP_400_BAD_REQUEST,
            errors: Optional[Dict] = None
    ) -> Response:
        """
        Generate a standardized error response.

        Args:
            message (str): An error message (default: "An error occurred").
            status_code (int): HTTP status code for the response (default: 400 Bad Request).
            errors (Optional[Dict]): Additional error details to include in the response.

        Returns:
            Response: A DRF Response object with the standardized error structure.
        """
        response: Dict[str, Any] = {
            "success": False,  # Indicates the request failed
            "message": message,  # Error message
        }

        if errors:
            response["errors"] = errors  # Add error details if provided

        return Response(response, status=status_code)

    @staticmethod
    def from_response(drf_response: Response) -> Response:
        """
        Convert a standard DRF response to a standardized API response.

        Useful for integrating with existing code that returns regular DRF responses.

        Args:
            drf_response (Response): A DRF Response object to be converted.

        Returns:
            Response: A standardized API response object.
        """
        if drf_response.status_code >= 400:
            return StandardResponse.error(
                message=drf_response.data.get('detail', 'An error occurred'),  # Extract error message or use default
                status_code=drf_response.status_code,  # Use the status code from the DRF response
                errors=drf_response.data  # Include the error details from the DRF response
            )
        return StandardResponse.success(
            data=drf_response.data,  # Include the data from the DRF response
            status_code=drf_response.status_code  # Use the status code from the DRF response
        )

"""
Renderers for standardizing DRF API responses.

This module provides renderers that automatically format API responses
according to the StandardResponse structure.
"""
from rest_framework import renderers

from drf_standardized_responses.responses import StandardResponse


class StandardResponseRenderer(renderers.JSONRenderer):
    """
    Custom renderer that formats all API responses using a standardized structure.

    This renderer ensures that all responses (both success and error) conform to the
    `StandardResponse` format, providing consistency across the API without requiring
    explicit wrapping in views.

    Features:
    - Automatically wraps successful responses in the `StandardResponse.success` format
    - Automatically wraps error responses in the `StandardResponse.error` format
    - Prevents double-wrapping of already formatted responses

    Usage:
        # In your settings.py
        REST_FRAMEWORK = {
            'DEFAULT_RENDERER_CLASSES': [
                'drf_standardized_responses.renderers.StandardResponseRenderer',
                ...
            ],
        }
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render the response data into the standardized API response format.

        Args:
            data (Any): The data to be rendered in the response.
            accepted_media_type (str, optional): The accepted media type for the response.
            renderer_context (dict, optional): Additional context for rendering, including the response object.

        Returns:
            bytes: The rendered response in JSON format.
        """
        # Extract the response object from the renderer context
        response = renderer_context.get('response', None) if renderer_context else None

        # If data already has the expected format structure, assume it's already been wrapped
        if isinstance(data, dict) and "success" in data and "message" in data:
            return super().render(data, accepted_media_type, renderer_context)

        # Handle error responses (status codes >= 400)
        if response and response.status_code >= 400:
            if isinstance(data, dict):
                message = data.pop('message', 'An error occurred')
                errors = data if data else None
            else:
                message = str(data) if data else 'An error occurred'
                errors = None

            return super().render(
                StandardResponse.error(
                    message=message,
                    status_code=response.status_code,
                    errors=errors
                ).data,
                accepted_media_type,
                renderer_context
            )

        # Handle success responses (status codes < 400)
        return super().render(
            StandardResponse.success(data=data).data,
            accepted_media_type,
            renderer_context
        )
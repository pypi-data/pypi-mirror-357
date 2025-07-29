# DRF Standardized Responses

## Overview

This package provides standardized response formatting for Django REST Framework projects. It includes:

- Custom renderers for consistent API responses
- Pagination classes that follow best practices
- Response utilities for error handling and success scenarios

## Installation

Follow the instructions in the README.rst file to install this package.

## Configuration

Add the following to your Django settings to use all features of this package:

```python
REST_FRAMEWORK = {
    # Exception handling for consistent error responses
    'EXCEPTION_HANDLER': 'drf_standardized_responses.exceptions.standardized_exception_handler',
    
    # Pagination with standardized format
    'DEFAULT_PAGINATION_CLASS': 'drf_standardized_responses.pagination.StandardizedPageNumberPagination',
    
    # Response rendering for consistent output structure
    'DEFAULT_RENDERER_CLASSES': [
        'drf_standardized_responses.renderers.StandardizedJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}
```

## Usage

### Renderers

Use our standardized renderer to ensure all responses follow a consistent format:
- Success responses will include `status`, `data`, and `message` fields
- Error responses will include `status`, `errors`, and `message` fields

### Pagination

Our pagination classes provide standardized output format with:
- Page information (current, total, etc.)
- Navigation links (next, previous)
- Result count information
- Consistent structure regardless of the pagination type

### Response Formatting

Use our response utility functions for consistent response structure:
- `success_response()` for 2xx responses
- `error_response()` for 4xx and 5xx responses

Each ensures proper status codes and consistent response structure.

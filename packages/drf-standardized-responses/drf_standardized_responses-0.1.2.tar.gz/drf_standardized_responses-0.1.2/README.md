# drf-standardized-responses

[![PyPI](https://img.shields.io/pypi/v/drf-standardized-responses.svg)](https://pypi.org/project/drf-standardized-responses/)
[![Downloads](https://static.pepy.tech/personalized-badge/drf-standardized-responses?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads)](https://pepy.tech/project/drf-standardized-responses)
[![Python Version](https://img.shields.io/pypi/pyversions/drf-standardized-responses.svg)](https://pypi.org/project/drf-standardized-responses/)
[![License](https://img.shields.io/badge/license-BSD-blue.svg)](LICENSE)

Standardized responses for Django REST Framework projects.

## Features

- **Consistent Response Format**: All API responses follow a standardized structure.
- **Custom Renderers**: JSON renderer that formats all responses with consistent structure.
- **Pagination**: Standardized pagination with consistent output format.
- **Response Utilities**: Helper functions for creating standard success and error responses.

## Installation

```bash
pip install drf-standardized-responses
```

## Quick Start

Add the necessary components to your Django REST Framework settings:

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

## Documentation

For more detailed documentation, see the [docs](./docs) directory.

## License

[BSD License](LICENSE)

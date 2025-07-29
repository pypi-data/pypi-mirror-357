drf-standardized-responses
==========================

Standardized responses for Django REST Framework projects.

Features
--------

* Consistent Response Format: All API responses follow a standardized structure.
* Custom Renderers: JSON renderer that formats all responses with consistent structure.
* Pagination: Standardized pagination with consistent output format.
* Response Utilities: Helper functions for creating standard success and error responses.

Installation
-----------

.. code-block:: bash

    pip install drf-standardized-responses

Quick Start
-----------

Add the necessary components to your Django REST Framework settings:

.. code-block:: python

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

Documentation
------------

Detailed documentation is in the "docs" directory.

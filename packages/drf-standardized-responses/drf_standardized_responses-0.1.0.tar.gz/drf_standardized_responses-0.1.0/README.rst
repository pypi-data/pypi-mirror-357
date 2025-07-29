.. image:: https://img.shields.io/pypi/v/drf-standardized-responses.svg
        :target: https://pypi.python.org/pypi/drf-standardized-responses

.. image:: https://img.shields.io/travis/user/repo.svg
        :target: https://travis-ci.org/user/repo

.. image:: https://readthedocs.org/projects/drf-standardized-responses/badge/?version=latest
        :target: https://drf-standardized-responses.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


drf-standardized-responses
==========================

A simple Django app to standardize responses for DRF projects.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "drf_standardized_responses" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'drf_standardized_responses',
    ]

2. Include the drf_standardized_responses URLconf in your project urls.py like this::

    path('responses/', include('drf_standardized_responses.urls')),

3. Run `python manage.py migrate` to create the drf_standardized_responses models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a response (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/responses/ to see your responses.


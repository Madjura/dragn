Installation
============

In the util package, set the paths in *paths.py*.
Because *dragn* uses Django, it is suggested to follow the Django deployment guides:

* `Deployment checklist`_
* `Deploy with wsgi`_

After starting the server that dragn is running on, create a new superuser::

   python manage.py createsuperuser

Use that user to login on the main page of dragn when opening it in the browser.
Only superusers have permission to upload and process new texts.


.. _Deployment checklist: https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/
.. _Deploy with wsgi: https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
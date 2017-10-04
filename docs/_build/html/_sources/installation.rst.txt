Installation
============
.. |br| raw:: html

   <br />
In the util package, set the paths in *paths.py*.
Because *dragn* uses Django, it is suggested to follow the Django deployment guides:

* `Deployment checklist`_
* `Deploy with wsgi`_

After starting the server that dragn is running on, create a new superuser::

   python manage.py createsuperuser

Use that user to login on the main page of dragn when opening it in the browser.
Only superusers have permission to upload and process new texts.

Then, create and initialize the database, see the Django docs if you want to use a legacy database: |br|
`python manage.py makemigrations` |br|
`python manage.py migrate` |br|
If you get an error message when opening the page in your browser, run additionally: |br|
`python manage.py makemigrations queryapp` |br|
It is unknown why this sometimes causes problems and sometimes not. |br|
Then create a new superuser: |br|
`python manage.py createsuperuser` and follow the instructions. |br|
Use that user to login on the main page of dragn when opening it in the browser. |br|
Only superusers have permission to upload and process new texts. |br|
After that, you need some `nltk` (http://www.nltk.org/) resources. To get them, run the following in a console (command prompt on Windows, terminal on Ubuntu for example): |br|
`$ python` |br|
`>>> import nltk` |br|
`>>> nltk.download()` |br|
Download the resources:
* punkt
* averaged perceptron
* wordnet
* stopwords

Alternatively you can select `all` and download all the resources. |br|
As the directory for the resources, choose one that your server running the system can find. Using Apache2 on Ubuntu 14.04 for example, that would be `/var/www/nltk_data`. If you are unsure, refer to the documentation of your server or try to run the system and check the error message for the directories it searched to find the resources, then move them there.

The system works only with .txt files with UTF-8 encoding. As it is not possible to automatically and perfectly detect the encoding of a text file and convert it the user must take care of this on their end and ensure the correct encoding. Encodings other than UTF-8 might work but will most likely not.





.. _Deployment checklist: https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/
.. _Deploy with wsgi: https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
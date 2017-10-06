# dragn
## Abstract
Close Reading is the process of analysing a text in-depth. The goal is to get as much information as possible in general or to focus on a specific aspect or question. Franco Moretti, an Italian literary scholar, coined the term "Distant Reading". The goal of "Distant Reading" means to gain understanding of texts by skimming the contents to gain a more general overview of the content. Due to the nature of Distant Reading, it is possible to process more content, faster, than would be possible with Close Reading. To do so by hand without the assistance of a tool is obviously very laborious and difficult. Machine assisted work in this area can be much more efficient.<br/>
This thesis is built and improved upon an existing system, dubbed [Skimmr](https://github.com/vitnov/SKIMMR), developed by Vit Novacek. The goal of the tool itself is to allow humans to effectively and efficiently perform Distant Reading on collections of texts or even just single texts. To accomplish this task, state-of-the-art technologies and frameworks are being used to improve the quality of the original system. The original system did not retain data of processed texts and thus after switching corpora the system would have to re-process the previous corpus. My system allows this and thus allows domain experts to work more efficiently and faster. The user interface in general is more streamlined and shows the user passages from the queried texts relevant to their query. The user can read previous and following passages from the same text for each found passage to gain additional understanding and context with minimal effort.<br/>
The new system, named "dragn", utilises a pipeline of four processing steps to create an information structure that users can query.<br/>
An arbitrary number of texts can be used and processed by the system. First the texts are parsed into paragraphs, Noun Phrases (NP) extracted and an inverse index of sentences is built. Using this index, a modified pointwise mutual information (PMI) value is calculated over the corpus. The classic PMI is calculated for the probability of two outcomes, in this case, the co-occurrence of two tokens in a given collection of texts. The modified PMI used in this system takes into account the frequency of the two tokens co-occurring and a calculated weighted distance between the two. This causes the score to be increased the more two tokens appear close to each other in a text. Performing the score calculation this way instead of using the classic PMI improves the quality of results for the Distant Reading. After building a vector space from the data in the previous step of the pipeline, relevant tokens are computed for each of the non-stopword tokens of the texts. Using the computed data, files are written to the disk to make it easier to perform queries on the data and to allow the data being used in different ways, such as a different front end.<br/>
Lastly, the results of the query are displayed to the user, whereas in the original system the results were static, "dragn" provides the data in JSON format and an interactive graph to easily allow experts to export and import the result data in their own systems.

## Installation
Python 3.5 or higher.<br/>
In the `util` package, set the paths in `paths.py`. Because dragn uses Django, it is suggested to follow the Django deployment guides:<br/>
[Deployment checklist](https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/)<br/>
[Deploy with wsgi](https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/)<br/>
Do not forget to check how to handle static files (Javascript and CSS):<br/>
[Managing static files (e.g. images, JavaScript, CSS)](https://docs.djangoproject.com/en/1.11/howto/static-files/)<br/>
The easiest way to handle the static files is to follow just this step:<br/>
[Deployment](https://docs.djangoproject.com/en/1.11/howto/static-files/#deployment)<br/>

Then, create and initialize the database, see the Django docs if you want to use a legacy database:<br/>
`python manage.py makemigrations`<br/>
`python manage.py migrate`<br/>
If you get an error message when opening the page in your browser, run additionally:<br/>
`python manage.py makemigrations queryapp`</br>
It is unknown why this sometimes causes problems and sometimes not.<br/>
Then create a new superuser:<br/>
`python manage.py createsuperuser` and follow the instructions.<br/>
Use that user to login on the main page of dragn when opening it in the browser.<br/>
Only superusers have permission to upload and process new texts.<br/>
After that, you need some `nltk` [Natural Language Toolkit](http://www.nltk.org/) resources. To get them, run the following in a console (command prompt on Windows, terminal on Ubuntu for example):<br/>
`$ python`<br/>
`>>> import nltk`<br/>
`>>> nltk.download()`<br/>
Download the resources:
* punkt
* averaged perceptron
* wordnet
* stopwords

Alternatively you can select `all` and download all the resources.<br/>
As the directory for the resources, choose one that your server running the system can find. Using Apache2 on Ubuntu 14.04 for example, that would be `/var/www/nltk_data`. If you are unsure, refer to the documentation of your server or try to run the system and check the error message for the directories it searched to find the resources, then move them there.

## Usage
To use the system, have it running on a server and navigate to it in the browser. Login using the superuser created as part of the installation and upload texts.<br>
### NOTE
The system works only with .txt files with UTF-8 encoding. As it is not possible to automatically and perfectly detect the encoding of a text file and convert it the user must take care of this on their end and ensure the correct encoding. Encodings other than UTF-8 might work but will most likely not.

## Celery
The following steps are optional but recommended.<br/>
Install Celery and RabbitMQ. Follow the instructions found in the documentation for Celery:<br/> http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#first-steps<br/> 
Turn on the usage of Celery in settings.py. Then, in the toplevel project folder (the one containing manage.py), run:<br/> 
`celery -A dragn worker -l info -P eventlet –pool=solo` in a console/terminal of your choice.<br/> 
If you do not want to or can not use Celery on your system, you can simply keep the `USE_CELERY` settings in `settings.py` set to False.<br/> 
Celery is used to allow you to check at what stage the processing of your texts is. After selecting texts for processing, you will see a task id on the processing page. Enter that in the form and submit it to see at which stage of the pipeline your text(s) are.<br/>


## Documentation
A documentation is included in the repository:<br/>
`docs/_build/html/index.html`<br/>
Or hosted on Github:<br/>
[Documentation](https://madjura.github.io/dragn/)

# dragn
## Abstract
Close Reading is the process of analysing a text in-depth. The goal is to get as much information as possible in general or to focus on a specific aspect or question. Franco Moretti, an Italian literary scholar, coined the term "Distant Reading". The goal of "Distant Reading" means to gain understanding of texts by skimming the contents to gain a more general overview of the content. Due to the nature of Distant Reading, it is possible to process more content, faster, than would be possible with Close Reading. To do so by hand without the assistance of a tool is obviously very laborious and difficult. Machine assisted work in this area can be much more efficient.<br/>
This thesis is built and improved upon an existing system, dubbed [Skimmr](https://github.com/vitnov/SKIMMR), developed by Vit Novacek. The goal of the tool itself is to allow humans to effectively and efficiently perform Distant Reading on collections of texts or even just single texts. To accomplish this task, state-of-the-art technologies and frameworks are being used to improve the quality of the original system. The original system did not retain data of processed texts and thus after switching corpora the system would have to re-process the previous corpus. My system allows this and thus allows domain experts to work more efficiently and faster. The user interface in general is more streamlined and shows the user passages from the queried texts relevant to their query. The user can read previous and following passages from the same text for each found passage to gain additional understanding and context with minimal effort.<br/>
The new system, named "dragn", utilises a pipeline of four processing steps to create an information structure that users can query.<br/>
An arbitrary number of texts can be used and processed by the system. First the texts are parsed into paragraphs, Noun Phrases (NP) extracted and an inverse index of sentences is built. Using this index, a modified pointwise mutual information (PMI) value is calculated over the corpus. The classic PMI is calculated for the probability of two outcomes, in this case, the co-occurrence of two tokens in a given collection of texts. The modified PMI used in this system takes into account the frequency of the two tokens co-occurring and a calculated weighted distance between the two. This causes the score to be increased the more two tokens appear close to each other in a text. Performing the score calculation this way instead of using the classic PMI improves the quality of results for the Distant Reading. After building a vector space from the data in the previous step of the pipeline, relevant tokens are computed for each of the non-stopword tokens of the texts. Using the computed data, files are written to the disk to make it easier to perform queries on the data and to allow the data being used in different ways, such as a different front end.<br/>
Lastly, the results of the query are displayed to the user, whereas in the original system the results were static, "dragn" provides the data in JSON format and an interactive graph to easily allow experts to export and import the result data in their own systems.

## Installation
In the `util` package, set the paths in `paths.py`. Because dragn uses Django, it is suggested to follow the Django deployment guides:<br/>
[Deployment checklist](https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/)<br/>
[Deploy with wsgi](https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/)
After starting the server that dragn is running on, create a new superuser:
`python manage.py createsuperuser`<br/>
Use that user to login on the main page of dragn when opening it in the browser.<br/>
Only superusers have permission to upload and process new texts.


## Documentation
A documentation is included in the repository:
`docs/_build/html/index.html`

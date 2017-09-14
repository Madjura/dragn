"""Forms for the queryapp. Contains forms for queries and processing texts."""
from django import forms
from django.forms import fields

from queryapp.models import TextsAlias


class QueryForm(forms.Form):
    """Form for the user queries."""
    # the query
    query = fields.CharField(max_length=100)
    # maximum number of nodes
    max_nodes = fields.IntegerField(min_value=1, required=False, initial=11)
    # maximum number of edges
    max_edges = fields.IntegerField(min_value=1, required=False, initial=100)
    # how many texts are to be returned in the result
    top_text_samples = fields.IntegerField(min_value=1, required=False, initial=10)
    # whether or not edges between non-query nodes are to be added and considered for the calculation or not
    lesser_edges = fields.BooleanField(required=False)
    # dropdown of the possible texts available for query
    texts = fields.ChoiceField(required=True,
                               help_text="Select text combination to process. If what you want is not here,"
                                         "process it first.",
                               )

    def __init__(self, *args, **kwargs):
        """
        Constructor.
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.fields["texts"].choices = [
            (alias.pk, alias.identifier) for alias in TextsAlias.objects.get_queryset().filter(processed=True)]

    def clean_query(self):
        """
        Cleans the query field.
        :return: The cleaned data.
        """
        return self.cleaned_data["query"].split(",")


class ProcessForm(forms.Form):
    """Form to initate the processing of texts with."""
    # the texts to be processed, multiple can be selected
    texts = fields.MultipleChoiceField(required=True, help_text="Select all texts to process.",
                                       widget=forms.CheckboxSelectMultiple())
    # the language of the texts
    language = fields.CharField(max_length=50, required=True, initial="english")

    def __init__(self, text_choices=None, *args, **kwargs):
        """
        Constructor.
        :param text_choices: The choices for the texts.
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        if text_choices:
            self.fields["texts"].choices = [(text, text) for text in text_choices]

from django import forms
from django.forms import fields

from queryapp.models import TextsAlias


class QueryForm(forms.Form):
    query = fields.CharField(max_length=100)
    max_nodes = fields.IntegerField(min_value=1, required=False, initial=25)
    max_edges = fields.IntegerField(min_value=1, required=False, initial=50)
    top_text_samples = fields.IntegerField(min_value=1, required=False, initial=10)
    lesser_edges = fields.BooleanField(required=False)
    texts = fields.ChoiceField(required=True,
                               help_text="Select text combination to process. If what you want is not here,"
                                         "process it first.",
                               )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["texts"].choices = [(alias.pk, alias.identifier) for alias in TextsAlias.objects.get_queryset()
            .filter(processed=True)]
        print(self.fields["texts"].choices)

    def clean_query(self):
        query_split = self.cleaned_data["query"].split(",")
        print(query_split)
        print(type(query_split))
        return self.cleaned_data["query"].split(",")


class ProcessForm(forms.Form):
    texts = fields.MultipleChoiceField(required=True, help_text="Select all texts to process.",
                                       widget=forms.CheckboxSelectMultiple())
    language = fields.CharField(max_length=50, required=True, initial="english")

    def __init__(self, text_choices=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if text_choices:
            self.fields["texts"].choices = [(text, text) for text in text_choices]

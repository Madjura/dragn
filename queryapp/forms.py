from django import forms
from django.forms import fields

class QueryForm(forms.Form):
    query = fields.CharField(max_length=100)
    max_nodes = fields.IntegerField(min_value=1, required=False, initial=25)
    max_edges = fields.IntegerField(min_value=1, required=False, initial=50)
    top_text_samples = fields.IntegerField(min_value=1, required=False, initial=10)
    
    def clean_query(self):
        return self.cleaned_data["query"].split(",")
from django import forms
from django.forms import fields

class QueryForm(forms.Form):
    query = fields.CharField(max_length=100)
    
    def clean_query(self):
        return self.cleaned_data["query"].split(",")
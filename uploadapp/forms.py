from django.core.exceptions import ValidationError
from django import forms
from multiupload.fields import MultiFileField


def file_size(value): # add this to some file where you can import it from
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 2 MiB.')
    
class UploadForm(forms.Form):
    files = MultiFileField(min_num=1, max_num=3, max_file_size=1024*1024*5)
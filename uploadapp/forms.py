from django import forms
from multiupload.fields import MultiFileField


class UploadForm(forms.Form):
    """Form for file uploads."""
    files = MultiFileField(min_num=1, max_num=3, max_file_size=1024 * 1024 * 5)

from django.core.files.storage import FileSystemStorage
from django.views.generic.edit import FormView

from uploadapp.forms import UploadForm


# Create your views here.
from util import paths


class UploadView(FormView):
    template_name = 'uploadapp/upload.html'
    form_class = UploadForm
    success_url = '/upload'

    def form_valid(self, form):
        for each in form.cleaned_data["files"]:
            fs = FileSystemStorage(location=paths.TEXT_PATH)
            _filename = fs.save(each.name, each)
            print(each.name)
        return super(UploadView, self).form_valid(form)

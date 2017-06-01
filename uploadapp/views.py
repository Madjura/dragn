from django.core.files.storage import FileSystemStorage
from django.views.generic.edit import FormView

from uploadapp.forms import UploadForm


# Create your views here.
class UploadView(FormView):
    template_name = 'uploadapp/upload.html'
    form_class = UploadForm
    success_url = '/upload'

    def form_valid(self, form):
        for each in form.cleaned_data["files"]:
            fs = FileSystemStorage()
            _filename = fs.save(each.name, each)
        return super(UploadView, self).form_valid(form)

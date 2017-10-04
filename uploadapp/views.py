"""Views for the uploadapp. Responsible for file uploads."""
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from uploadapp.forms import UploadForm


# Create your views here.
from util import paths


class UploadView(FormView):
    """Classview for fileupload."""
    # upload template
    template_name = 'uploadapp/upload.html'
    # upload form
    form_class = UploadForm
    success_url = reverse_lazy('upload')

    def form_valid(self, form):
        """
        Function to check validity of the form.
        :param form: The form.
        :return: The rendered view for the upload success.
        """
        for each in form.cleaned_data["files"]:
            fs = FileSystemStorage(location=paths.TEXT_PATH)
            fs.save(each.name, each)
        return super(UploadView, self).form_valid(form)

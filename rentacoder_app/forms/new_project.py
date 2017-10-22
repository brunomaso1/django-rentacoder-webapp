from django.forms import ModelForm

from rentacoder_app.models import Project


class NewProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'technologies', 'openings', 'start_date', 'end_date']

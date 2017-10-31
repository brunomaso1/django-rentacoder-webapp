from django import forms
from rentacoder_app.models import Project, JobOffer, User, ProjectQuestion


class NewProjectForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.SelectDateWidget())
    end_date = forms.DateField(widget=forms.SelectDateWidget())

    class Meta:
        model = Project
        exclude = ('user',)


class ApplyToProjectForm(forms.ModelForm):
    class Meta:
        model = JobOffer
        exclude = ('user', 'project')


class ProjectQuestionForm(forms.ModelForm):
    class Meta:
        model = ProjectQuestion
        fields = ('question',)


class AnswerQuestionForm(forms.ModelForm):
    class Meta:
        model = ProjectQuestion
        fields = ('answer',)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'technologies', 'avatar')


class RegisterForm(forms.Form):
    """
    Form used to register a new user
    """
    first_name = forms.CharField(max_length=40, required=True, label="First name")
    last_name = forms.CharField(max_length=40, required=True, label="Last name")
    username = forms.CharField(max_length=40, required=True)
    email = forms.EmailField()
    password = forms.CharField(required=True, widget=forms.PasswordInput())
    password_confirmation = forms.CharField(widget=forms.PasswordInput(), required=True, label="Confirm password")

    def is_valid(self):
        valid = super(RegisterForm, self).is_valid()
        return valid and self.cleaned_data.get('password') == self.cleaned_data.get('password_confirmation')


class ResetPasswordForm(forms.Form):
    """
    Form used to reset password
    """
    token = forms.CharField(widget=forms.HiddenInput())
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirmation = forms.CharField(widget=forms.PasswordInput())

    def is_valid(self):
        valid = super(ResetPasswordForm, self).is_valid()
        return valid and self.cleaned_data.get('password') == self.cleaned_data.get('password_confirmation')

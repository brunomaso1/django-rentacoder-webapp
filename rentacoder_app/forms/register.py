from django import forms


class RegisterForm(forms.Form):
    """
    Form used to reset password
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

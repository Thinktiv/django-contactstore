from django import forms


class ContactImportForm(forms.Form):
    """Specifies the contract for the addressbook download."""

    email    = forms.EmailField()
    password = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.widgets.PasswordInput()
        )

    def clean_email(self):
        email = self.cleaned_data['email']
        if email.endswith('@googlemail.com'):
            email = email.replace('@googlemail.com', '@gmail.com')
        return email

    def clean(self):
        super(forms.Form, self).clean()
        if not self.cleaned_data.get("email"):
            raise ValidationError("please enter your email address")

        # Do we need to change this rule to qualify yahoo? (or any other oauth provider)
        # If we are yahoo we SHOULD get back an access token, this would replace a password
        # With it we can do YQL
        # We should probably make sure we know what the provider was as well
        if not self.cleaned_data.get("password"):
            raise ValidationError("please enter your password")
        return self.cleaned_data


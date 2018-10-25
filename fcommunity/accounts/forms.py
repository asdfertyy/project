from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required = True)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            # 'address',
            # 'birthday',
            'password1',
            'password2'
        )

        def save(self, commit = True):
            user = super(RegistrationForm, self).save(commit = False)
            user.first_name = cleaned_data('first_name')
            user.last_name = cleaned_data('last_name')
            user.email = cleaned_data('email')
            # user.address = cleaned_data('address')
            # user.birthday = cleaned_data('birthday')

            if commit:
                user.save()

            return user
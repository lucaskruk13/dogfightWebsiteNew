from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django.core.validators import RegexValidator
from string import Template
from django.forms import ImageField
from django.utils.safestring import mark_safe





class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email','first_name','last_name', 'password1', 'password2')

class ProfileForm(forms.ModelForm):
    handicap = forms.CharField(max_length=6, required=True, validators=[
        RegexValidator(
            regex="^[+]?\d*\.?\d*$",
            message="Invalid Handicap",
            code='invalid_handicap'
        )
    ])

    bio = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows':5, 'placeholder':'Tell others about you'}
        ),
        max_length=4000,
        help_text='Max Length: 4000'
    )

    # TODO: Edit Profile Tests
    # TODO: Fix Signup Not Creating Scores - Add check when signing to see if scores/handicap has been created successfully.


    class Meta:
        model = Profile
        fields = ('handicap','bio')




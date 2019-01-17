from django import forms
from accounts.models import Scores

class DogfightSignupForm(forms.ModelForm):

    class Meta:
        model = Scores
        fields = ()
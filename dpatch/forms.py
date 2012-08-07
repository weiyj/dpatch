from django import forms

from dpatch.models import ExceptFile

class GitRepoForm(forms.Form):
    name = forms.CharField(max_length = 30)
    user = forms.CharField(max_length = 30)
    email = forms.CharField(max_length = 30)
    url = forms.CharField(max_length = 256)

class ExceptFileForm(forms.ModelForm):
    class Meta:
        model = ExceptFile
        fields = ['type', 'file', 'reason']

from django import forms

from dpatch.models import ExceptFile, Patch, Report, Type

class GitRepoForm(forms.Form):
    name = forms.CharField(max_length = 30)
    user = forms.CharField(max_length = 30)
    email = forms.CharField(max_length = 30)
    url = forms.CharField(max_length = 256)

class ExceptFileForm(forms.ModelForm):
    class Meta:
        model = ExceptFile
        fields = ['type', 'file', 'reason']

class PatchNewForm(forms.ModelForm):
    class Meta:
        model = Patch
        fields = ['tag', 'type', 'file']

    def __init__(self, **kwargs):
        super(PatchNewForm, self).__init__(**kwargs)
        self.fields['type'].queryset = Type.objects.filter(id__lte = 10000)

class ReportNewForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['tag', 'type', 'file']

    def __init__(self, **kwargs):
        super(ReportNewForm, self).__init__(**kwargs)
        self.fields['type'].queryset = Type.objects.filter(id__gt = 10000)
from django import forms
from assets.models import Action


class ServiceForm(forms.ModelForm):

    class Meta:
        model = Action
        fields = ['incident', 'act_detail', 'result']

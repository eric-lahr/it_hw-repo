from django import forms
from assets.models import Action


class ServiceForm(forms.ModelForm):

    class Meta:
        model = Action
        fields = ['incident', 'act_detail', 'result']

class LocationCheckForm(forms.Form):
    location = forms.CharField(max_length=15,
            required=True,
            label="Location")

    assets = forms.CharField(widget=forms.Textarea,
                             required=True,
                             label="Assets at location")

    def clean(self):
        self.cleaned_data = super().clean()
#        self.cleaned_data['location'] = 'location'
#        self.cleaned_data['assets'] = 'assets'
        return self.cleaned_data



        
#        cleaned_data = super().clean()
#        loc = cleaned_data['location']
#        eq = cleaned_data['assets']
#        print(eq)
#        cleaned_data['loc_to_check'] = loc
#        cleaned_data['e_to_check'] = eq
#        return cleaned_data

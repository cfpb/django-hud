from django import forms

class HudForm(forms.Form):
    zipcode = forms.IntegerField(label='ZipCode', min_value=00501, max_value=99951,)
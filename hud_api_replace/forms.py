from django import forms
from localflavor.us.forms import USZipCodeField

class HudForm(forms.Form):
    zipcode = USZipCodeField()  

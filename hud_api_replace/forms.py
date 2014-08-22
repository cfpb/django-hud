from django import forms
from django.contrib.localflavor.us.forms import USZipCodeField

class HudForm(forms.Form):
    zipcode = USZipCodeField()  

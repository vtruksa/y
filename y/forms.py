from django import forms
from datetime import datetime

class CardForm(forms.Form):
    number = forms.IntegerField(max_value=9999999999999999, required=True)
    exp_month = forms.IntegerField(max_value=12, required=True)
    exp_year = forms.IntegerField(min_value=datetime.now().year)
    cvc = forms.IntegerField(min_value=000, max_value=999)
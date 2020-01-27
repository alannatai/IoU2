from .models import Household
from django.forms import ModelForm

class HouseholdForm(ModelForm):
    class Meta:
        model = Household
        fields = ["name", "member"]

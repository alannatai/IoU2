
from .models import Household
from django.forms import ModelForm

class HouseholdForm(ModelForm):
    class Meta:
        model = Household
        fields = ["name", "members"]

from django.forms import ModelForm
from .models import Expense

class ExpenseForm(ModelForm):
    class Meta:
        model = Expense
        fields = ['name', 'cost', 'description']

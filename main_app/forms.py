from django.forms import ModelForm
from .models import Household, Expense

class HouseholdForm(ModelForm):
    class Meta:
        model = Household
        fields = ["name", "members"]

class ExpenseForm(ModelForm):
    class Meta:
        model = Expense
        fields = ['name', 'cost', 'description']

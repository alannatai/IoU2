from django.db import models

from django.contrib.auth.models import User

#Household model
class Household(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

#Users
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    household = models.ManyToManyField(Household)
    # budgetb
    
    def __str__(self):
        return self.name

#Expenses
class Expense(models.Model):
    member = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    cost = models.FloatField(blank=True, default=None)
    date = models.DateField()
    description = models.CharField(max_length=100)
    household = models.ForeignKey(Household, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.who_paid} bought {self.name} for {self.cost}"

#Expense Split
class Split(models.Model):
    amount_owed = models.FloatField()
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)

    def __str__(self):
        return f"You owe {lender_name} ${expense_cost}."
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from django.urls import reverse

class Household(models.Model):
    name = models.CharField(max_length=50)
    # need this to be able to edit on both ends
    members = models.ManyToManyField('Member', through='Member_households', related_name="members")

    def __str__(self):
        return f"Household: {self.name}"

class Member(AbstractUser):
    households = models.ManyToManyField(Household, related_name="households")
    avatar = models.CharField(max_length=200, default="/static/images/no_avatar.webp")

    def __str__(self):
        return f"Member: {self.username}"

    def get_absolute_url(self):
        return reverse('user_update', kwargs={'pk': self.id})

class Expense(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cost = models.FloatField(blank=True, default=None)
    date = models.DateTimeField(default=datetime.now, blank=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.member.username} added {self.name} for {self.cost}"

    def get_absolute_url(self):
        return reverse("households_details", kwargs={"household_id": self.household.pk})


class Split(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    has_paid = models.BooleanField(default=False)
    amount_owed = models.FloatField()

    def __str__(self):
        return f"{self.member.username} needs to pay ${self.amount_owed} for {self.expense.name}."

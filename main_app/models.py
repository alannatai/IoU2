from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime

class Household(models.Model):
    name = models.CharField(max_length=50)
    # need this to be able to edit on both ends
    member = models.ManyToManyField('Member', through='Member_household', related_name="members")

    def __str__(self):
        return f"Household: {self.name}"

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    household = models.ManyToManyField(Household, related_name="households")
    # budgetb

    def __str__(self):
        return f"Member: {self.user}"

# 'signals' so our Member model will auto create/update when User is created/updated
@receiver(post_save, sender=User)
def create_user_member(sender, instance, created, **kwargs):
    if created:
        Member.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_member(sender, instance, **kwargs):
    instance.member.save()

class Expense(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cost = models.FloatField(blank=True, default=None)
    date = models.DateTimeField(default=datetime.now, blank=True)
    description = models.CharField(max_length=100)
    household = models.ForeignKey(Household, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.member.user.username} bought {self.name} for {self.cost}"

class Split(models.Model):
    amount_owed = models.FloatField()
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    has_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.member.user.username} needs to pay ${self.amount_owed} for {self.expense.name}."

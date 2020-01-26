from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Household(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"Household: {self.name}"

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    household = models.ManyToManyField(Household)
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
    date = models.DateField()
    description = models.CharField(max_length=100)
    household = models.ForeignKey(Household, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.who_paid} bought {self.name} for {self.cost}"

class Split(models.Model):
    amount_owed = models.FloatField()
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.member} needs to pay ${self.amount_owed} for {self.expense.name}."

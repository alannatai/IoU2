from django.contrib import admin
from .models import Household, Member, Expense, Split


# Register your models here.
admin.site.register(Household)
admin.site.register(Member)
admin.site.register(Expense)
admin.site.register(Split)

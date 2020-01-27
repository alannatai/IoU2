from django.contrib import admin
from .models import Household, Member, Expense

admin.site.register(Household)
admin.site.register(Member)
admin.site.register(Expense)

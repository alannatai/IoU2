from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from guardian.admin import GuardedModelAdmin

from .models import Household, Member, Expense, Split

class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Member

class MyUserAdmin(GuardedModelAdmin):
    form = MyUserChangeForm
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('households', 'avatar')}),
    )

# Register your models here.
admin.site.register(Member, MyUserAdmin)
admin.site.register(Household)
admin.site.register(Expense)
admin.site.register(Split)

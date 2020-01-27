from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('about/', views.about, name='about'),
  path('households/', views.household_index, name='household_index'),
  path('households/<int:household_id>', views.household_details, name='household_details'),
  path('households/<int:household_id>/<int:expense_id>', views.expense_details, name='expense_details'),

  path('accounts/signup/', views.signup, name='signup')
]

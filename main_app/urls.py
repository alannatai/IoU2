from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('about/', views.about, name='about'),
  path('households/', views.households_index, name='households_index'),
  path('households/create/', views.HouseholdCreate.as_view(), name='households_create'),
  path('households/<int:household_id>', views.households_details, name='households_details'),
  path('households/<int:household_id>/new_expense/', views.new_expense, name='new_expense'),
  path('households/<int:household_id>/<int:expense_id>/', views.expense_details, name='expense_details'),
  path('accounts/signup/', views.signup, name='signup')
]

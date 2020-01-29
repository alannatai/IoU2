from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('about/', views.about, name='about'),
  path('households/', views.households_index, name='households_index'),
  path('households/create/', views.HouseholdCreate.as_view(), name='households_create'),
  path('households/<int:household_id>/', views.households_details, name='households_details'),
  path('households/<int:household_id>/<int:expense_id>/', views.expenses_detail, name='expenses_detail'),
  path('households/<int:household_id>/<int:pk>/edit/', views.ExpenseUpdate.as_view(), name='expense_update'),
  path('households/<int:household_id>/<int:expense_id>/delete/', views.remove_expense, name='remove_expense'),
  path('households/<int:household_id>/update/', views.households_update, name='households_update'),
  path('households/<int:household_id>/add_expense/', views.add_expense, name='add_expense'),
  path('households/<int:household_id>/<int:member_id>/has_paid/', views.has_paid, name='has_paid'),
  path('households/<int:household_id>/<int:split_id>/has_paid_split/', views.has_paid_split, name='has_paid_split'),
  path('users/<int:pk>/update/', views.UserUpdate.as_view(), name='user_update'),
  path('accounts/signup/', views.signup, name='signup')
]

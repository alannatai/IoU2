from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('about/', views.about, name='about'),
  path('households/', views.households_index, name='households_index'),
  path('households/create/', views.HouseholdCreate.as_view(), name='households_create'),


  path('accounts/signup/', views.signup, name='signup')
]


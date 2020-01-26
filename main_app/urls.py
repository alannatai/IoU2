from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('households/', views.households_index, name='households_index'),

  path('accounts/signup/', views.signup, name='signup')
]


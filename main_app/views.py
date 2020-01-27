from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .models import Household

def home(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")


@login_required
def household_index(request):
    print(request.user.id)
    households = Household.objects.filter(member=request.user.id)
    return render(request, 'households/index.html', {
        'user': request.user,
        'households': households
    })

@login_required
def household_details(request, household_id):
    household = Household.objects.get(pk=household_id)
    return render(request, 'households/details.html', {
        'user': request.user,
        'household': household
    })

def expense_details(request, household_id, expense_id):
    pass

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('households_index')
        else:
            error_message = 'Invalid sign up. Please try again.'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

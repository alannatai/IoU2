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
def households_index(request):
    print(request.user.id)
    households = Household.objects.filter(member=request.user.id)
    return render(request, 'households/index.html', {
        'user': request.user,
        'households': households
    })

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

def delete_household(request):
    households = Household.objects.filter()
    return render(request, households/index.html",{
        
    })
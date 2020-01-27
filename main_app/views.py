from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Household

def home(request):
    return render(request, 'index.html')
    
def about(request):
    return render(request, 'about.html')


@login_required
def households_index(request):
    print(request.user.id)
    member = Member.objects.get(user = request.user.id)
    return render(request, 'households/index.html', {
        'user': request.user,
        'member': member
    })

@login_required
def households_details(request, household_id):
    household = Household.objects.get(pk=household_id)
    return render(request, 'households/details.html', {
        'user': request.user,
        'household': household
    })

@login_required
def create_expense(request, household_id, user):
    household = Household.objects.get(pk=household_id)
    user = request.user

def expense_details(request, household_id, expense_id):
    expense = Expense.objects.get(id=expense_id)
    return render(request, 'expense/details.html', {
        'user': request.user,
        'expense': expense / expense.household.member_set.count
    })

def new_expense(request):
    return render(request, 'expense/new.html')

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

# def delete_household(request):
#     households = Household.objects.filter()
#     return render(request, households/index.html",{
        
#     })

class HouseholdCreate(LoginRequiredMixin, CreateView):
    model = Household
    fields = ['name']
    success_url = '/households/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

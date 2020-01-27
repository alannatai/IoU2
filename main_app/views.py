from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ExpenseForm

from .models import Household, Member, Expense

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

@login_required
def households_index(request):
    member = Member.objects.get(user=request.user.id)
    households = Household.objects.filter(member=member.id)
    return render(request, 'households/index.html', {
        'user': request.user,
        'households': households
    })

@login_required
def households_details(request, household_id):
    household = Household.objects.get(pk=household_id)
    expense_form = ExpenseForm()
    return render(request, 'households/details.html', {
        'user': request.user,
        'household': household,
        'expense_form': expense_form
    })

@login_required
def households_update(request, household_id):
    if request.method == "POST":
        household = Household.objects.get(pk=household_id)
        form = HouseholdForm(request.POST, instance=household)
        # validate the form
        if form.is_valid():
            form.save()
        return redirect('households_details', household_id=household_id)
    household = Household.objects.get(id=household_id)
    household_form = HouseholdForm(initial={
        "name": household.name,
        "member": household.member.all()
    })
    return render(request, 'households/update.html', {
        # pass the cat and feeding_form as context
        'household': household, 'household_form': household_form
    })

def expenses_details(request, household_id, expense_id):
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

# def delete_household(request):
#     households = Household.objects.filter()
#     return render(request, households/index.html",{

#     })

class HouseholdCreate(LoginRequiredMixin, CreateView):
    model = Household
    fields = ['name']
    success_url = '/households/'

    def form_valid(self, form):
        new_household = form.save()
        Member.objects.get(user__id=self.request.user.id).household.add(new_household.id)
        return super().form_valid(form)

@login_required
def add_expense(request, household_id):
  form = ExpenseForm(request.POST)
  if form.is_valid():
    member = Member.objects.get(user__id=request.user.id)
    new_expense = form.save(commit=False)
    new_expense.member_id = member.id
    new_expense.household_id = household_id
    new_expense.save()
  return redirect('households_details', household_id=household_id)

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from .forms import HouseholdForm, ExpenseForm

from .models import Household, Member, Expense, Split

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

def get_owed(household_id, current_user_id):
    ### calculates total of expenses owed without subtracting what they owe the user###
    # members_owed = []
    # members = Household.objects.get(id=household_id).member.all()
    # for member in members:
    #     member_owed_obj = { 'member_owed': member.user, 'amount_owed': 0 }
    #     expenses_owed = Expense.objects.filter(household=household_id, member=member.id)
    #     for expense in expenses_owed:
    #         for value in Split.objects.filter(expense=expense.id, member=current_user_id).values('amount_owed'):
    #             member_owed_obj['amount_owed'] += value['amount_owed'] 
    #     members_owed.append(member_owed_obj)

    # how much you owe people will be positive, if negative, that means people owe you
    oweDict = { }
    # iterate through all expenses in household
    for expenseRow in Expense.objects.filter(household=household_id):
        # if user paid for expense
        if expenseRow.member.id == current_user_id:
          # check the splits under that expense
            for splitRow in Split.objects.filter(expense=expenseRow.id):
              # add members to oweDict if they dont exist and subtract what they owe you
                if not splitRow.member.user in oweDict:
                    oweDict[splitRow.member.user] = 0 
                oweDict[splitRow.member.user] -= splitRow.amount_owed
        # if someone else paid for expense
        else:
            for splitRow in Split.objects.filter(expense=expenseRow.id):
                # this split is you, add what the member owes you
                if splitRow.member.id == current_user_id:
                    if not expenseRow.member.user in oweDict:
                      # add member to oweDict if they dont exist
                        oweDict[expenseRow.member.user] = 0 
                        # add what they owe you
                    oweDict[expenseRow.member.user] += splitRow.amount_owed
    return oweDict
          

@login_required
def households_details(request, household_id):
    household = Household.objects.get(pk=household_id)
    expense_form = ExpenseForm()
    member = Member.objects.get(user__id=request.user.id)
    oweDict = get_owed(household_id, member.id)
    print(oweDict.items())
    return render(request, 'households/details.html', {
        'user': request.user,
        'household': household,
        'expense_form': expense_form,
        'oweDict': oweDict.items()
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

@login_required
def create_expense(request, household_id, user):
    household = Household.objects.get(pk=household_id)
    user = request.user

def expenses_detail(request, household_id, expense_id):
    expense = Expense.objects.get(id=expense_id)
    return render(request, 'expense/details.html', {
        'user': request.user,
        'expense': expense 
    })

def remove_expense(request, household_id, expense_id):
    expense = Expense.objects.remove(id=expense_id)
    return render(request, "expense/", {
        'user': request.user,
        'expense': expense 
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
        household_members = new_expense.household.member.exclude(user=request.user)
        AMOUNTOWED = new_expense.cost / (household_members.count() + 1)
        for member in household_members:
            new_split = Split(amount_owed=AMOUNTOWED, member=member, expense=new_expense)
            print(new_split)
            new_split.save()
    return redirect('households_details', household_id=household_id)

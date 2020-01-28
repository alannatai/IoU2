from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import HouseholdForm, ExpenseForm

from .models import Household, Member, Expense, Split

# custom form for signup
class MemberCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = Member
        fields = ('username', 'email')

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

@login_required
def households_index(request):
    households = Member.objects.get(id=request.user.id).households.all()
    return render(request, 'households/index.html', {
        'user': request.user,
        'households': households
    })

def users_detail(request, member_id):
  return render(request, 'users/details.html', {
    'user': request.user
  })

def get_owed(household_id, current_user_id):
    # how much you owe people will be positive, if negative, that means people owe you
    ledger = { }
    
    for expense_row in Expense.objects.filter(household=household_id):
        if expense_row.member.id == current_user_id:
            for split_row in Split.objects.filter(expense=expense_row.id):
                if split_row.has_paid == False:
                    if not split_row.member in ledger:
                        ledger[split_row.member] = 0
                    ledger[split_row.member] -= split_row.amount_owed
        else:
            for split_row in Split.objects.filter(expense=expense_row.id):
                if split_row.has_paid == False:
                    if split_row.member.id == current_user_id:
                        if not expense_row.member in ledger:
                            ledger[expense_row.member] = 0
                        ledger[expense_row.member] += split_row.amount_owed
    return ledger

def has_paid(request, household_id, member_id):
    print('household_id', household_id)
    print('member_id', member_id)
    for expense_row in Expense.objects.filter(household=household_id):
        if expense_row.member.id == request.user.id or expense_row.member.id == member_id:
            for split_row in Split.objects.filter(expense=expense_row.id):
                if split_row.member.id == member_id or split_row.member.id == request.user.id:
                    split_row.has_paid = True
                    split_row.save()
    return redirect('households_details', household_id=household_id)

@login_required
def households_details(request, household_id):
    household = Household.objects.get(pk=household_id)
    expense_form = ExpenseForm()
    ledger = get_owed(household_id, request.user.id)
    return render(request, 'households/details.html', {
        'user': request.user,
        'household': household,
        'expense_form': expense_form,
        'ledger': ledger.items()
    })

@login_required
def households_update(request, household_id):
    if request.method == "POST":
        household = Household.objects.get(pk=household_id)
        form = HouseholdForm(request.POST, instance=household)
        if form.is_valid():
            form.save()
        return redirect('households_details', household_id=household_id)
    household = Household.objects.get(id=household_id)
    household_form = HouseholdForm(initial={
        "name": household.name,
        "members": household.members.all()
    })
    return render(request, 'households/update.html', {
        'household': household, 'household_form': household_form
    })

def expenses_detail(request, household_id, expense_id):
    expense = Expense.objects.get(id=expense_id)
    household = Household.objects.get(id=household_id)
    member = Member.objects.all(id=member_id)
    return render(request, 'expense/details.html', {
        # 'user': request.user,
        'expense': request.expense.get(id=expense_id),
        'household': request.household.member.all(),
        'member': request.split.all(),
    })

def remove_expense(request, household_id, expense_id):
    expense = Expense.objects.remove(id=expense_id)
    return render(request, "expense/", {
        'user': request.user,
        'expense': expense
    })

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = MemberCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('households_index')
        else:
            error_message = 'Invalid sign up. Please try again.'
    form = MemberCreationForm()
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
        Member.objects.get(id=self.request.user.id).households.add(new_household.id)
        return super().form_valid(form)

@login_required
def add_expense(request, household_id):
    form = ExpenseForm(request.POST)
    if form.is_valid():
        member = Member.objects.get(id=request.user.id)
        new_expense = form.save(commit=False)
        new_expense.member_id = request.user.id
        new_expense.household_id = household_id
        new_expense.save()
        household_members = new_expense.household.members.exclude(id=request.user.id)
        AMOUNTOWED = new_expense.cost / (household_members.count() + 1)
        for member in household_members:
            new_split = Split(amount_owed=AMOUNTOWED, member=member, expense=new_expense)
            print(new_split)
            new_split.save()
    return redirect('households_details', household_id=household_id)

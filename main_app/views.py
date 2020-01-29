from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .forms import HouseholdForm, ExpenseForm

from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm

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

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = MemberCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # need to explicitly state backend since we have 2 authentication backends (ref. settings.py @ AUTHENTICATION_BACKENDS)
            login(request, user, backend="django.contrib.auth.backendsModelBackend")
            return redirect('households_index')
        else:
            error_message = 'Invalid sign up. Please try again.'
    form = MemberCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

@login_required
def households_index(request):
    households = request.user.households.all()
    return render(request, 'households/index.html', {
        'user': request.user,
        'households': households
    })

@login_required
def users_detail(request, member_id):
  return render(request, 'users/details.html', {
    'user': request.user
  })

# helper function
def get_owed(household_id, current_user_id):
    # how much you owe people will be positive, if negative, that means people owe you
    ledger = { }

    # get all splits in household by iterating through each expense on the household
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

# helper function
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


class HouseholdCreate(LoginRequiredMixin, CreateView):
    model = Household
    fields = ['name']
    success_url = '/households/'

    def form_valid(self, form):
        new_household = form.save()
        self.request.user.households.add(new_household.id)
        # create two groups of permissions for household
        # admins have full CRUD authorization, regular members only read access (+ full CRUD authorization for expenses they create under this household)
        household_group = Group.objects.create(name=f'household_{new_household.id}')
        household_admins_group = Group.objects.create(name=f'household_{new_household.id}_admins')
        assign_perm("view_household", household_group, new_household)
        assign_perm("view_household", household_admins_group, new_household)
        assign_perm("change_household", household_admins_group, new_household)
        assign_perm("add_household", household_admins_group, new_household)
        assign_perm("delete_household", household_admins_group, new_household)
        self.request.user.groups.add(household_group)
        self.request.user.groups.add(household_admins_group)
        return super().form_valid(form)


@login_required
def households_details(request, household_id):
    household = Household.objects.get(pk=household_id)
    if request.user.has_perm("view_household", household):
        expense_form = ExpenseForm()
        ledger = get_owed(household_id, request.user.id)
        return render(request, 'households/details.html', {
            'user': request.user,
            'household': household,
            'expense_form': expense_form,
            'ledger': ledger.items(),
        })
    else:
        return HttpResponse(status=403)

@login_required
def households_update(request, household_id):
    household = Household.objects.get(pk=household_id)
    if request.user.has_perm("change_household", household):
        if request.method == "POST":
            form = HouseholdForm(request.POST, instance=household)
            if form.is_valid():
                form.save()
            return redirect('households_details', household_id=household_id)
        household_form = HouseholdForm(initial={
            "name": household.name,
            "members": household.members.all()
        })
        return render(request, 'households/update.html', {
            'household': household, 'household_form': household_form
        })
    else:
        return HttpResponse(status=403)

# TODO
# def delete_household(request):
#     households = Household.objects.filter()
#     return render(request, households/index.html",{
#     })

@login_required
def add_expense(request, household_id):
    household = Household.objects.get(pk=household_id)
    if request.user.has_perm("view_household", household):
        form = ExpenseForm(request.POST)
        if form.is_valid():
            new_expense = form.save(commit=False)
            new_expense.member_id = request.user.id
            new_expense.household_id = household_id
            new_expense.save()
            # give expense creator permission to update/delete
            # add and view permissions on expenses are not needed for any authenticaed user since we assume if they can view the household they have those permissions
            assign_perm("change_expense", request.user, new_expense)
            assign_perm("delete_expense", request.user, new_expense)
            household_members = new_expense.household.members.exclude(id=request.user.id)
            AMOUNTOWED = new_expense.cost / (household_members.count() + 1)
            for member in household_members:
                new_split = Split(amount_owed=AMOUNTOWED, member=member, expense=new_expense)
                new_split.save()
        return redirect('households_details', household_id=household_id)
    else:
        return HttpResponse(status=403)

@login_required
def expenses_detail(request, household_id, expense_id):
    household = Household.objects.get(id=household_id)
    if request.user.has_perm("view_household", household):
        expense = Expense.objects.get(id=expense_id)
        split = Split.objects.filter(expense=expense_id)
        return render(request, 'expense/details.html', {
            'expense': expense,
            'household': household,
            'split': split,
        })
    else:
        return HttpResponse(status=403)

@login_required
def remove_expense(request, household_id, expense_id):
    # if request.user.has_perm("delete_expense", expense):
    # TODO
    expense = Expense.objects.remove(id=expense_id),
    return render(request, "expense/", {
        'user': request.user,
        'expense': expense
    })

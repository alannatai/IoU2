from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .forms import HouseholdForm, ExpenseForm

from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm, remove_perm

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
            # assign member permissions
            assign_perm("view_member", user, user)
            assign_perm("change_member", user, user)
            assign_perm("delete_member", user, user)
            # need to explicitly state backend since we have 2 authentication backends (refer to settings.py -> AUTHENTICATION_BACKENDS variable)
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

class UserUpdate(LoginRequiredMixin, UpdateView):
    model = Member
    fields = ['username', 'email', 'first_name', 'last_name']

    def dispatch(self, request, *args, **kwargs):
        requested_user = self.get_object()
        current_user = request.user
        print(current_user.has_perm("view_member", requested_user))
        if current_user.has_perm("view_member", requested_user):
            return super(UserUpdate, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponse(status=401)

# helper function
def get_owed(household_id, current_user_id):
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

def has_paid_split(request, household_id, split_id):
    print('split_id', split_id)
    split = Split.objects.get(id=split_id)
    print(split)
    split.has_paid = True
    split.save()
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
        ledger = get_owed(household_id, request.user.id).items()
        sorted_ledger = sorted(ledger, key=lambda item: item[1])
        ledger_splits = { }

        for member, amount in ledger:
            member_splits = list(Split.objects.filter(expense__member=member.id, member=request.user.id, has_paid=False))
            user_splits = list(Split.objects.filter(expense__member=request.user.id, member=member.id, has_paid=False))
            ledger_splits[member] = member_splits + user_splits
        is_admin = request.user.has_perm("change_household", household)

        return render(request, 'households/details.html', {
            'user': request.user,
            "is_admin": is_admin,
            'household': household,
            'expense_form': expense_form,
            'sorted_ledger': sorted_ledger,
            'ledger_splits': ledger_splits.items()
        })
    else:
        return HttpResponse(status=401)

@login_required
def households_update(request, household_id):
    household = Household.objects.get(pk=household_id)
    if request.user.has_perm("change_household", household):
        if request.method == "POST":
            previous_household_members = household.members.all()
            household_group = Group.objects.get(name=f'household_{household_id}')
            form = HouseholdForm(request.POST, instance=household)
            if form.is_valid():
                new_household_members = form.cleaned_data["members"].all()
                removed_members = previous_household_members.difference(new_household_members)
                for removed_member in removed_members:
                    # user cant remove self from household
                    if removed_member.id == request.user.id:
                        return HttpResponse(status=403)
                    household_group.user_set.remove(removed_member)
                added_members = new_household_members.difference(previous_household_members)
                for added_member in added_members:
                    household_group.user_set.add(added_member)
                form.save()
            return redirect('households_details', household_id=household_id)
        # GET request
        household_form = HouseholdForm(initial={
            "name": household.name,
            "members": household.members.all()
        })
        return render(request, 'households/update.html', {
            'household': household, 'household_form': household_form
        })
    else:
        return HttpResponse(status=401)

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
        return HttpResponse(status=401)

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
        return HttpResponse(status=401)

@login_required
def remove_expense(request, household_id, expense_id):
    # if request.user.has_perm("delete_expense", expense):
    # TODO
    expense = Expense.objects.remove(id=expense_id),
    return render(request, "expense/", {
        'user': request.user,
        'expense': expense
    })

def expense_splits(request, household_id, member_id):
    user_splits = Split.objects.filter(expense__member=request.user.id, member=member_id, has_paid=False)
    member_splits = Split.objects.filter(expense__member=member_id, member=request.user.id, has_paid=False)
    ledger = get_owed(household_id, request.user.id)
    return render(request, 'expense/splits.html', {
        'user_splits': user_splits,
        'member_splits': member_splits,
        'member': Member.objects.get(id=member_id),
        'ledger': ledger.items()
    })

class ExpenseView(CreateView):
    template_name = 'expense/details.html'
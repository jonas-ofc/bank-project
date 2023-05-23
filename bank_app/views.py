from django.shortcuts import render, reverse, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from .models import Customer, LoanRequest, AccountRequest, Ledger, Account, ApprovedLoanRequests, ApprovedAccountRequests, Rank
from .forms import LoanRequestForm, AccountRequestForm, UserForm, CustomerForm, TransferForm
from django.db import IntegrityError, transaction
from secrets import token_urlsafe


@login_required
def index(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('bank_app:admin_page'))
    else:
        return HttpResponseRedirect(reverse('bank_app:customer_dashboard'))


@login_required
def admin_page(request):
    customers = Customer.objects.all()
    users = User.objects.all()
    loan_requests = LoanRequest.objects.all()
    account_requests = AccountRequest.objects.all()
    approved_loan_requests = ApprovedLoanRequests.objects.all()
    accounts = Account.objects.all()
    context = {
        'customers': customers,
        'accounts': accounts,
        'approved_loan_requests': approved_loan_requests,
        'users': users,
        'loan_requests': loan_requests,
        'account_requests': account_requests,
    }
    return render(request, 'bank_app/admin_page.html', context)


@login_required
def customer_dashboard(request, id=''):
    if request.user.is_staff:
        customer = Customer.objects.get(user=id)
    else:
        customer = Customer.objects.get(user=request.user)
    rank = customer.rank
    loan_requests = LoanRequest.objects.filter(customer=customer)
    account_requests = AccountRequest.objects.filter(customer=customer)
    accounts = Account.objects.filter(customer=customer)
    admin_customer = True if request.user.is_staff and customer.user == request.user else False
    context = {
        'admin_customer': admin_customer,
        'customer': customer,
        'accounts': accounts,
        'rank': rank,
        'loan_requests': loan_requests,
        'account_requests': account_requests,
    }

    return render(request, 'bank_app/dashboard.html', context)


@login_required
def make_loan_request(request):
    if request.method == 'POST':
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            LoanRequest.objects.create(customer=request.user.customer, loan_amount=request.POST['loan_amount'])
            return HttpResponseRedirect(reverse('bank_app:customer_dashboard'))
        else:
            form = LoanRequestForm()
            context = {
                'error': '* Please enter a positive loan ammount',
            }
            return render(request, 'bank_app/make_loan_request.html', context)
    return render(request, 'bank_app/make_loan_request.html')


@login_required
def make_account_request(request):
    customer = request.user.customer
    form = AccountRequestForm(initial={'customer': customer})
    if request.method == 'POST':
        form = AccountRequestForm(request.POST)
        if form.is_valid():
            customer = form.cleaned_data["customer"]
            try:
                AccountRequest.objects.create(customer=customer)
                return HttpResponseRedirect(reverse('bank_app:customer_dashboard'))
            except IntegrityError:
                return IntegrityError
        else:
            return render(request, 'bank_app/make_account_request.html', {'form': form})
    else:
        return render(request, 'bank_app/make_account_request.html', {'form': form})


@login_required
@require_http_methods(['DELETE'])
def decline_loan_request(request, id):
    loan_request = get_object_or_404(LoanRequest, id=id)
    try:
        loan_request.delete()
        return HttpResponse("<button disabled>Declined</button>", content_type="text/html")
    except IntegrityError:
        return HttpResponse(status_code=500)


@login_required
@require_http_methods(['POST'])
def approve_loan_request(request, id):
    try:
        loan_request = get_object_or_404(LoanRequest, id=id)
        with transaction.atomic():
            loan_request.status = "approved"
            loan_request.save()
            # If customer has accout use transfer to that account, if not create an account
            if Account.objects.filter(customer=loan_request.customer).exists():
                customer_account = Account.objects.filter(customer=loan_request.customer).first()
            else:
                customer_account = Account.objects.create(customer=loan_request.customer, title="Account 1", is_loan=False)
            # create account for loan
            loan_i = Account.objects.filter(customer=loan_request.customer, is_loan=True).count() + 1
            loan_account = Account.objects.create(customer=loan_request.customer, title=f"Loan {loan_i}", is_loan=True)
            # add loan_requests to approved_loan_requests
            ApprovedLoanRequests.objects.create(
                loan_request=loan_request, account=loan_account, approved_by=request.user)
            # information for ledger
            amount = loan_request.loan_amount
            debit_account = loan_account
            debit_text = "Approved " + loan_account.title
            credit_account = customer_account
            credit_text = "Approved " + loan_account.title

            # create ledger
            Ledger.transfer(amount, debit_account, debit_text, credit_account, credit_text)

            return HttpResponse("<button disabled>Approved</button>", content_type="text/html")
    except IntegrityError:
        return HttpResponse(status_code=500)


@login_required
@require_http_methods(['DELETE'])
def decline_account_request(request, id):
    account_request = get_object_or_404(AccountRequest, id=id)
    try:
        account_request.delete()
        return HttpResponse("<button disabled>Declined</button>", content_type="text/html")
    except IntegrityError:
        return HttpResponse(status_code=500)


@login_required
@require_http_methods(['POST'])
def approve_account_request(request, id):
    try:
        account_request = get_object_or_404(AccountRequest, id=id)
        with transaction.atomic():
            account_request.status = "approved"
            account_request.save()

            # create account for account, and account for use
            account = Account.objects.create(customer=account_request.customer, title="Account")

            # add account_requests to approved_account_requests
            ApprovedAccountRequests.objects.create(account_request=account_request, account=account, approved_by=request.user)

            return HttpResponse("<button disabled>Approved</button>", content_type="text/html")
    except IntegrityError:
        return HttpResponse(status_code=500)


@login_required
def review_loan_request(request):

    loan_request = LoanRequest.objects.all()
    context = {
        'loan_request': loan_request
    }
    return render(request, 'bank_app/review_loan_request.html', context)


@login_required
def add_customer(request):
    if request.user.is_staff:
        user_form = UserForm()
        customer_form = CustomerForm()

        context = {
            'user_form': user_form,
            'customer_form': customer_form
        }

        if request.method == 'POST':
            user_form = UserForm(request.POST)
            customer_form = CustomerForm(request.POST)
            if user_form.is_valid() and customer_form.is_valid():
                username = user_form.cleaned_data["username"]
                first_name = user_form.cleaned_data["first_name"]
                last_name = user_form.cleaned_data["last_name"]
                email = user_form.cleaned_data["email"]
                password = token_urlsafe(16)
                phone = customer_form.cleaned_data["phone"]
                rank = customer_form.cleaned_data["rank"]
                try:
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        first_name=first_name,
                        last_name=last_name
                    )
                    print(f'********** Username: {username} -- Password: {password}')
                    Customer.objects.create(user=user, rank=rank, phone=phone)
                    return admin_page(request)
                except IntegrityError:
                    context['error_msg'] = 'User could not be created, please try again'
                    return render(request, 'bank_app/add_customer.html', context)
            else:
                context["errors"] = user_form.errors
                return render(request, 'bank_app/add_customer.html', context)
        else:
            return render(request, 'bank_app/add_customer.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))


@login_required
def customer_overview(request):
    if request.user.is_staff:
        customers = Customer.objects.all()
        context = {
            'customers': customers,
        }
        return render(request, 'bank_app/customer_overview.html', context)
    else:
        return HttpResponseRedirect(reverse('bank_app:customer_dashboard'))


@login_required
def search_customers(request):
    assert request.user.is_staff, 'Customer user routing staff view.'
    search_term = request.GET['search']
    customers = Customer.objects.all()
    if len(search_term) == 0:
        customers = Customer.objects.all()
    else:
        customers = Customer.search(search_term)
    context = {
        'customers': customers,
    }
    rendered = render_to_string('bank_app/partials/search_customer_results.html', context)
    return HttpResponse(rendered)


@login_required
def account_details(request, id=''):
    account = get_object_or_404(Account, id=id)
    customer = account.customer
    context = {
        'account': account,
        'customer': customer
    }
    # Check if staff or users match
    if request.user.is_staff is True or request.user == customer.user:
        return render(request, 'bank_app/account_details.html', context)
    else:
        return HttpResponseRedirect(reverse('bank_app:customer_dashboard'))


@login_required
def make_transfer(request):
    if request.method == 'POST':
        form = TransferForm(request.POST, user=request.user)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            debit_account = form.cleaned_data['debit_account']
            debit_text = form.cleaned_data['debit_text']
            credit_account = form.cleaned_data['credit_account']
            credit_text = form.cleaned_data['credit_text']
            Ledger.transfer(amount=amount, debit_account=debit_account, debit_text=debit_text, credit_account=credit_account, credit_text=credit_text)
            return HttpResponseRedirect(reverse('bank_app:customer_dashboard'))

    else:
        form = TransferForm(user=request.user)
    return render(request, 'bank_app/make_transfer.html', {'form': form})


@login_required
def change_rank(request, id):
    if request.method == 'POST':
        customer = Customer.objects.get(pk=id)
        match request.POST['selected_rank']:
            case 'Basic':
                customer.rank = Rank(1)
            case 'Silver':
                customer.rank = Rank(2)
            case 'Gold':
                customer.rank = Rank(3)
            case _:
                return HttpResponseBadRequest()
        try:
            customer.save()
            updated_customer = Customer.objects.get(pk=id)
            context = {
                'customer': customer,
                'updated_customer': updated_customer,
            }

            return render(request, 'bank_app/partials/rank_selector.html', context)
        except IntegrityError:
            return HttpResponse(status_code=500)

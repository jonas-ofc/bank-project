from __future__ import annotations
from decimal import Decimal
from django.db import models, transaction
from django.db.models.query import QuerySet
from django.db.models import Q
from django.contrib.auth.models import User
from datetime import datetime
from django.conf import settings


class Bank(models.Model):
    name = models.CharField(max_length=20, unique=True, default=settings.REMOTE_IP[0]['name'])
    ip_address = models.GenericIPAddressField(default=settings.REMOTE_IP[0]['address'])


class UID(models.Model):
    @classmethod
    @property
    def uid(cls):
        return cls.objects.create()

    def __str__(self):
        return f'{self.pk}'


class Rank(models.Model):
    name = models.CharField(max_length=50, unique=True)
    value = models.IntegerField(unique=True)
    description = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name}'


class Customer(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.PROTECT)
    rank = models.ForeignKey(Rank, on_delete=models.PROTECT)
    phone = models.CharField(max_length=15, db_index=True)

    @property
    def full_name(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

    @property
    def customer_name(self) -> str:
        return self.full_name if self.full_name != "" else self.user.username

    @property
    def accounts(self) -> QuerySet:
        return Account.objects.filter(customer=self)

    @property
    def account_count(self) -> int:
        return self.accounts.filter(is_loan=False).count()

    @property
    def loan_count(self) -> int:
        return self.accounts.filter(is_loan=True).count()

    @classmethod
    def search(cls, search_term):
        return cls.objects.filter(
            Q(user__username__icontains=search_term) |
            Q(user__first_name__icontains=search_term) |
            Q(user__last_name__icontains=search_term) |
            Q(user__email__icontains=search_term) |
            Q(phone__contains=search_term)
        )[:15]


class LoanRequest(models.Model):

    STATUS_CHOICES = [
        ("not reviewed", "not reviewed"),
        ("approved", "approved"),
        ("declined", "declined"),
    ]
    status = models.CharField(
        max_length=25, db_index=True, choices=STATUS_CHOICES, default="not reviewed")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)


class AccountRequest(models.Model):
    STATUS_CHOICES = [
        ("not reviewed", "not reviewed"),
        ("approved", "approved"),
        ("declined", "declined"),
    ]
    status = models.CharField(
        max_length=25, db_index=True, choices=STATUS_CHOICES, default="not reviewed")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)


class Account(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    title = models.CharField(max_length=15, db_index=True)
    is_loan = models.BooleanField(default=False)
    # approved_by = models.CharField(max_length=255, db_index=True)
    # created_at  = models.DateTimeField(auto_now_add=True, db_index=True)

    @property
    def movements(self) -> QuerySet:
        return Ledger.objects.filter(account=self)

    @property
    def balance(self) -> Decimal:
        return self.movements.aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)

    def __str__(self):
        return f'{self.pk} :: {self.customer} :: {self.title} :: {self.is_loan}'


class ApprovedLoanRequests(models.Model):
    loan_request = models.ForeignKey(LoanRequest, on_delete=models.PROTECT)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT)


class ApprovedAccountRequests(models.Model):
    account_request = models.ForeignKey(AccountRequest, on_delete=models.PROTECT)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT)


class Transaction(models.Model):
    datetime = models.DateTimeField(db_index=True, default=datetime.now)

    class Meta:
        # sort by "datetime" in descending order unless
        # overridden in the query with order_by()
        ordering = ['-datetime']

    @classmethod
    @property
    def uid(cls):
        return cls.objects.create()

    @property
    def earlier_transactions(self) -> QuerySet:
        return Transaction.objects.filter(datetime__lte=self.datetime)

    def __str__(self):
        return f'{self.pk}'


class Ledger(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.PROTECT)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=25, decimal_places=2)
    message = models.TextField(max_length=40)

    class Meta:
        ordering = ['transaction']

    @classmethod
    def transfer(cls, amount, debit_account, debit_text, credit_account, credit_text, is_loan=True) -> int:
        assert amount >= 0, 'Only a positive amount is allowed for transfer'
        with transaction.atomic():
            if is_loan:
                uid = Transaction.uid
                cls(amount=-amount, transaction=uid,
                    account=debit_account, message=debit_text).save()
                cls(amount=amount, transaction=uid,
                    account=credit_account, message=credit_text).save()
            else:
                raise ValueError(f'Error: Insufficient funds for {amount} dollars')
            return uid

    @property
    def balance_at_time(self) -> QuerySet:
        account_ledgers = Ledger.objects.filter(account=self.account)
        earlier_trans = self.transaction.earlier_transactions
        account_earlier_trans = []
        for a in account_ledgers:
            for e in earlier_trans:
                if a.transaction == e and a not in account_earlier_trans:
                    account_earlier_trans.append(a)
        return sum(transaction.amount for transaction in account_earlier_trans)

    def __str__(self):
        return f'Message: {self.message}, Amount: {self.amount}, Account: {self.account}, Transaction: {self.transaction}, Created at: {self.transaction.datetime}'

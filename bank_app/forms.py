from django import forms
from .models import Customer, Account
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


class LoanRequestForm(forms.Form):

    # Ensure loan_amount is positive

    loan_amount = forms.DecimalField(min_value=0)

    def clean_loan_amount(self):
        loan_amount = self.cleaned_data['loan_amount']
        if loan_amount < 0:
            raise forms.ValidationError("Please enter a positive loan amount.")
        return loan_amount


class AccountRequestForm(forms.Form):
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), widget=forms.HiddenInput())


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ["phone", "rank"]


class AccountModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.id} - {obj.title} ({obj.balance} DKK)'


class TransferForm(forms.Form):
    amount = forms.DecimalField(max_digits=25, decimal_places=2)
    debit_account = AccountModelChoiceField(queryset=Account.objects.all())
    debit_text = forms.CharField()
    credit_account = forms.IntegerField(label="Recipient account number:")
    credit_text = forms.CharField()

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        customer = Customer.objects.get(user=user)
        self.fields['debit_account'].queryset = Account.objects.filter(customer=customer, is_loan=False)

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        debit_account = cleaned_data.get('debit_account')
        credit_account_id = cleaned_data.get('credit_account')

        if amount and debit_account and amount > debit_account.balance:
            self.add_error('amount', 'Amount exceeds balance of selected account.')

        if credit_account_id:
            credit_account = get_object_or_404(Account, id=credit_account_id)
            cleaned_data['credit_account'] = credit_account

        return cleaned_data

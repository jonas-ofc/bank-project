from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bank_app.models import Rank, Customer, LoanRequest, AccountRequest, Bank
from django.conf import settings


class Command(BaseCommand):
    def handle(self, **options):
        # check if ranks already exist
        print('Provisioning with default customer ranks and banks...')
        if not Rank.objects.all():
            Rank(name="Basic", value=25).save()
            Rank(name="Silver", value=50).save()
            Rank(name="Gold", value=75).save()
        else:
            print('One or more ranks already exist, stopped provisioning')
        if not Bank.objects.all():
            for i in settings.REMOTE_IP:
                name = i['name']
                ip_address = i['address']
                Bank(name=name, ip_address=ip_address).save()
        else:
            print('One or more banks already exist, stopped provisioning')

        if settings.DEBUG:
            print('Adding demo data...')
            if not AccountRequest.objects.all():
                # create bank admin:
                bank_admin = User.objects.create_user('adam', email='adam@admin.com', password='adampass123')
                bank_admin.first_name = 'Adam'
                bank_admin.last_name = 'Administrator'
                bank_admin.is_staff = True
                bank_admin.save()
                # create bank customer:
                john_user = User.objects.create_user('john', email='john@john.com', password='johnpass123')
                john_user.first_name = 'John'
                john_user.last_name = 'Doe'
                john_user.save()
                john_customer = Customer(user=john_user, rank=Rank.objects.get(pk=3), phone='12345678')
                john_customer.save()
                # create loan requests for the customer:
                loan_requests = [
                    LoanRequest(customer=john_customer, loan_amount=1000),
                    LoanRequest(customer=john_customer, loan_amount=2000),
                    LoanRequest(customer=john_customer, loan_amount=3000),
                ]
                for loan_request in loan_requests:
                    loan_request.save()

                # create account requests for the customer:
                account_requests = [
                    AccountRequest(customer=john_customer),
                    AccountRequest(customer=john_customer),
                    AccountRequest(customer=john_customer),
                ]
                for account_request in account_requests:
                    account_request.save()

                print('Demo data generated successfully.')
            else:
                print('Data already exists, skipped generating.')

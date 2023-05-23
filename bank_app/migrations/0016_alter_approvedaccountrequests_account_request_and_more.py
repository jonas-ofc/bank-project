# Generated by Django 4.1.7 on 2023-04-26 21:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0015_accountrequest_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approvedaccountrequests',
            name='account_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bank_app.accountrequest'),
        ),
        migrations.AlterField(
            model_name='approvedloanrequests',
            name='loan_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bank_app.loanrequest'),
        ),
    ]

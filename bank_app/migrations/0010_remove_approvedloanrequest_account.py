# Generated by Django 4.1.7 on 2023-04-21 23:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0009_remove_account_created_at_remove_account_is_approved_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='approvedloanrequest',
            name='account',
        ),
    ]
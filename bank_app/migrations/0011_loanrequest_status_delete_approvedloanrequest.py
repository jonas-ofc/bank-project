# Generated by Django 4.1.7 on 2023-04-22 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0010_remove_approvedloanrequest_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanrequest',
            name='status',
            field=models.CharField(choices=[('not reviewed', 'not reviewed'), ('accepted', 'accepted'), ('declined', 'declined')], db_index=True, default='not reviewed', max_length=25),
        ),
        migrations.DeleteModel(
            name='ApprovedLoanRequest',
        ),
    ]

# Generated by Django 4.1.7 on 2023-03-23 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0003_loanrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loanrequest',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]

# Generated by Django 4.1.7 on 2023-03-23 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0004_alter_loanrequest_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loanrequest',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]

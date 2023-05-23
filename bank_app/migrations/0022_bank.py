# Generated by Django 4.1.7 on 2023-05-22 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0021_alter_ledger_options_alter_transaction_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Filip', max_length=20, unique=True)),
                ('ip_address', models.GenericIPAddressField(default='139.144.178.18')),
            ],
        ),
    ]
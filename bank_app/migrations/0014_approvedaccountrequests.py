# Generated by Django 4.1.7 on 2023-04-26 19:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bank_app', '0013_uid'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApprovedAccountRequests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bank_app.account')),
                ('account_request', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bank_app.accountrequest')),
                ('approved_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

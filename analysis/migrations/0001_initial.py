# Generated by Django 5.0.2 on 2024-03-31 18:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('positive', models.DecimalField(decimal_places=20, max_digits=20)),
                ('negative', models.DecimalField(decimal_places=20, max_digits=20)),
                ('neutral', models.DecimalField(decimal_places=20, max_digits=20)),
                ('result', models.DecimalField(decimal_places=20, max_digits=20)),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='User_Result', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

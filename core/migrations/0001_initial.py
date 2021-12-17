# Generated by Django 3.0.9 on 2020-12-15 05:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=200, null=True)),
                ('last_name', models.CharField(max_length=200, null=True)),
                ('email', models.CharField(max_length=200, null=True)),
                ('profile_picture', models.ImageField(blank=True, default='yoda.png', null=True, upload_to='')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('league_name', models.CharField(max_length=30)),
                ('league_id', models.CharField(max_length=10)),
                ('league_commissioner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commissioner', to=settings.AUTH_USER_MODEL)),
                ('league_members', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

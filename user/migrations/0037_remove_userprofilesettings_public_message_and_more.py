# Generated by Django 4.2.6 on 2023-11-11 19:29

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0036_userprofilesettings_filter_tag"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofilesettings",
            name="public_message",
        ),
        migrations.RemoveField(
            model_name="userprofilesettings",
            name="public_tags",
        ),
        migrations.RemoveField(
            model_name="userprofilesettings",
            name="two_factor",
        ),
        migrations.RemoveField(
            model_name="userprofilesettings",
            name="two_factor_enabled",
        ),
        migrations.RemoveField(
            model_name="userprofilesettings",
            name="two_factor_method",
        ),
    ]

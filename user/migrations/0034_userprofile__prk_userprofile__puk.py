# Generated by Django 4.2.6 on 2023-10-28 10:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0033_userprofilesettings_two_factor_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="_prk",
            field=models.BinaryField(default=b""),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="_puk",
            field=models.BinaryField(default=b""),
        ),
    ]

# Generated by Django 4.2.6 on 2023-10-16 11:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0019_userprofile_premium_id_userprofile_premium_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatmessage",
            name="time_sent",
            field=models.DateField(auto_now_add=True),
        ),
    ]

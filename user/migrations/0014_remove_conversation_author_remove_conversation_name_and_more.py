# Generated by Django 4.2.6 on 2023-10-12 10:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0013_conversation_author_alter_conversation_users"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="conversation",
            name="author",
        ),
        migrations.RemoveField(
            model_name="conversation",
            name="name",
        ),
        migrations.AlterField(
            model_name="conversation",
            name="users",
            field=models.ManyToManyField(
                max_length=2, related_name="users", to="user.userprofile"
            ),
        ),
    ]
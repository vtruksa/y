# Generated by Django 4.2.6 on 2023-11-05 10:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("post", "0016_post_profanity"),
        ("user", "0035_remove_userprofilesettings_user_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofilesettings",
            name="filter_tag",
            field=models.ManyToManyField(to="post.tag"),
        ),
    ]
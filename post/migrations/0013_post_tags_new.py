# Generated by Django 4.2.6 on 2023-10-22 21:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("post", "0012_post__visibility_alter_post_author_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="tags_new",
            field=models.ManyToManyField(
                editable=False, related_name="tags", to="post.tag"
            ),
        ),
    ]

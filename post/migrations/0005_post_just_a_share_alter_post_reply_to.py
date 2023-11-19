# Generated by Django 4.2.6 on 2023-10-16 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("post", "0004_post_liked_post_reply_to"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="just_a_share",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="post",
            name="reply_to",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="reply",
                to="post.post",
            ),
        ),
    ]
# Generated by Django 4.2.6 on 2023-10-19 10:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("post", "0009_tag_posts"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tag",
            options={"ordering": ["popularity"]},
        ),
    ]

# Generated by Django 2.2.9 on 2021-11-24 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0005_auto_20211124_1605"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="image",
            field=models.ImageField(
                blank=True, upload_to="posts/", verbose_name="Картинка"
            ),
        ),
    ]

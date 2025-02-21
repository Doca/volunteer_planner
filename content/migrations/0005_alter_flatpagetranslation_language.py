# Generated by Django 4.0.3 on 2022-03-30 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0004_alter_flatpagetranslation_language"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flatpagetranslation",
            name="language",
            field=models.CharField(
                choices=[
                    ("uk", "Ukrainian"),
                    ("en", "English"),
                    ("de", "German"),
                    ("cs", "Czech"),
                    ("el", "Greek"),
                    ("fr", "French"),
                    ("hu", "Hungarian"),
                    ("pl", "Polish"),
                    ("pt", "Portuguese"),
                    ("ru", "Russian"),
                    ("sv", "Swedish"),
                    ("tr", "Turkish"),
                ],
                max_length=20,
                verbose_name="language",
            ),
        ),
    ]

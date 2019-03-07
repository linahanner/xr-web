# Generated by Django 2.1.7 on 2019-02-24 21:31

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("wagtailcore", "0041_group_collection_permissions_verbose_name_plural")
    ]

    operations = [
        migrations.CreateModel(
            name="StandardPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.Page",
                    ),
                ),
                ("content", wagtail.core.fields.StreamField([])),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        )
    ]
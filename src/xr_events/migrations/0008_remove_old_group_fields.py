# Generated by Django 2.1.7 on 2019-03-26 13:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("xr_events", "0007_data_populate_eventpage_startdate_and_enddate")]

    operations = [
        migrations.RemoveField(model_name="eventgrouppage", name="is_regional_group"),
        migrations.RemoveField(model_name="eventgrouppage", name="local_group"),
        migrations.AlterField(
            model_name="eventgrouppage",
            name="group",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT, to="xr_pages.LocalGroup"
            ),
        ),
        migrations.AlterField(
            model_name="eventpage",
            name="group",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="events",
                to="xr_pages.LocalGroup",
            ),
        ),
    ]
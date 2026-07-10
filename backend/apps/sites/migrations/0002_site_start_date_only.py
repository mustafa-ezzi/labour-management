from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sites", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="site",
            name="from_date",
            field=models.DateField(help_text="Site starting date."),
        ),
        migrations.AlterField(
            model_name="site",
            name="to_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]

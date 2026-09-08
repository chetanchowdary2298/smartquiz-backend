from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="topic",
            field=models.CharField(max_length=100, default="General"),
            preserve_default=False,
        ),
    ]

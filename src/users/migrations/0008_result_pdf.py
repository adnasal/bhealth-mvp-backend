# Generated by Django 3.2.12 on 2023-03-06 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_user_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='pdf',
            field=models.FileField(default='src/results/Patient Medical History Report.pdf', upload_to='pdf'),
        ),
    ]

# Generated by Django 2.0.3 on 2018-05-01 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0003_auto_20180425_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activerecord',
            name='active',
            field=models.IntegerField(choices=[(0, '预约'), (1, '借阅'), (2, '归还')]),
        ),
    ]

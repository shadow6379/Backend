# Generated by Django 2.0.3 on 2018-04-24 15:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='AttitudeRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attitude', models.IntegerField(choices=[(0, '点赞'), (1, '踩'), (2, '举报')])),
                ('report_reason', models.IntegerField(choices=[(0, '广告或垃圾信息'), (1, '低俗或色情'), (2, '违反相关法律法规或管理规定'), (3, '辱骂或不友善'), (4, '引战或过于偏激的主观判断'), (5, '泄露他人隐私'), (6, '与作品或讨论区主题无关'), (7, '刷屏'), (8, '刷屏')], null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BookInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cover', models.ImageField(null=True, upload_to='uploads')),
                ('name', models.CharField(max_length=255)),
                ('author', models.CharField(max_length=255)),
                ('score', models.IntegerField(default=0)),
                ('brief', models.TextField()),
                ('ISBN', models.CharField(max_length=16, unique=True)),
                ('publish_time', models.CharField(max_length=20)),
                ('press', models.CharField(max_length=32)),
                ('contents', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='BookInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.IntegerField(choices=[(0, '正常'), (1, '被预订'), (2, '被借出')])),
                ('bid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_instances', to='user_app.BookInfo')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_time', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('bid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_app.BookInfo')),
                ('parent_comment', models.ForeignKey(default='0', on_delete=django.db.models.deletion.CASCADE, to='user_app.Comment')),
            ],
        ),
        migrations.CreateModel(
            name='ScoreToBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(choices=[(1, '1星'), (2, '2星'), (3, '3星'), (4, '4星'), (5, '5星')])),
                ('bid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_app.BookInfo')),
            ],
        ),
        migrations.CreateModel(
            name='TypeInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(height_field=150, null=True, upload_to='', width_field=150)),
                ('gender', models.NullBooleanField()),
                ('phone', models.CharField(max_length=20, null=True)),
                ('auth', models.BinaryField(default=False)),
                ('auth_info', models.CharField(max_length=255, null=True)),
                ('real_name', models.CharField(max_length=20, null=True)),
                ('other', models.TextField(null=True)),
                ('collections', models.ManyToManyField(related_name='book_collectors', to='user_app.BookInfo')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='scoretobook',
            name='uid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_app.UserInfo'),
        ),
        migrations.AddField(
            model_name='comment',
            name='uid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_app.UserInfo'),
        ),
        migrations.AddField(
            model_name='bookinfo',
            name='types',
            field=models.ManyToManyField(related_name='related_books', to='user_app.TypeInfo'),
        ),
        migrations.AddField(
            model_name='attituderecord',
            name='cid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_app.Comment'),
        ),
        migrations.AddField(
            model_name='attituderecord',
            name='uid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_app.UserInfo'),
        ),
        migrations.AlterUniqueTogether(
            name='scoretobook',
            unique_together={('uid', 'bid')},
        ),
        migrations.AlterUniqueTogether(
            name='attituderecord',
            unique_together={('cid', 'uid')},
        ),
    ]
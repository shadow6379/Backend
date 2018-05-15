from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# Create your models here.


class TypeInfo(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class BookInfo(models.Model):
    # showed in the home page
    cover = models.ImageField(upload_to="uploads", null=True)
    name = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    score = models.IntegerField(default=0)
    brief = models.TextField()

    ISBN = models.CharField(max_length=16, unique=True)
    publish_time = models.CharField(max_length=20)
    press = models.CharField(max_length=32)
    contents = models.TextField()

    types = models.ManyToManyField(to=TypeInfo, related_name='related_books')

    def __str__(self):
        return self.name


class UserInfo(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    """
    user.username
    user.password
    user.email
    """

    avatar = models.ImageField(height_field=150, width_field=150, null=True)
    # true for male, false for female
    gender = models.NullBooleanField(null=True)
    # user's phone number, default = ''
    phone = models.CharField(max_length=20, null=True)
    # the user is authentication or not
    auth = models.BooleanField(default=False)
    # auth = models.BinaryField(default=False)
    auth_info = models.CharField(max_length=255, null=True)
    real_name = models.CharField(max_length=20, null=True)
    # other information, such as introduction
    other = models.TextField(null=True)

    collections = models.ManyToManyField(to=BookInfo, related_name='book_collectors')

    def __str__(self):
        return self.user.username


class ScoreToBook(models.Model):
    # user id
    uid = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE)
    # book id
    bid = models.ForeignKey(to=BookInfo, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('uid', 'bid')

    score_choices = (
        (1, u'1星'),
        (2, u'2星'),
        (3, u'3星'),
        (4, u'4星'),
        (5, u'5星'),
    )
    score = models.IntegerField(choices=score_choices)


class Comment(models.Model):
    # user id
    uid = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE)
    # book id
    bid = models.ForeignKey(to=BookInfo, on_delete=models.CASCADE)

    comment_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    """
    use AttitudeRecord table to get these fields, or the data may be inconsistent

    agree_times = models.IntegerField(default=0)
    disagree_times = models.IntegerField(default=0)
    reported_times = models.IntegerField(default=0)
    """

    # '0' means that this comment is a root comment
    parent_comment = models.ForeignKey(to='self', on_delete=models.CASCADE, default='0')


class AttitudeRecord(models.Model):
    # comment id
    cid = models.ForeignKey(to=Comment, on_delete=models.CASCADE)
    # user id
    uid = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('cid', 'uid')

    attitude_choices = (
        (0, u'点赞'),
        (1, u'踩'),
        (2, u'举报'),
    )
    attitude = models.IntegerField(choices=attitude_choices)

    report_reason_choices = (
        (0, u'广告或垃圾信息'),
        (1, u'低俗或色情'),
        (2, u'违反相关法律法规或管理规定'),
        (3, u'辱骂或不友善'),
        (4, u'引战或过于偏激的主观判断'),
        (5, u'泄露他人隐私'),
        (6, u'与作品或讨论区主题无关'),
        (7, u'刷屏'),
        (8, u'其它原因'),
    )
    report_reason = models.IntegerField(choices=report_reason_choices, null=True)

    def clean(self):
        if self.attitude == 2 and self.report_reason is None:
            raise ValidationError('missing reasons for reporting')


class BookInstance(models.Model):
    bid = models.ForeignKey(to=BookInfo, on_delete=models.CASCADE, related_name='book_instances')

    state_choices = (
        (0, u'正常'),
        (1, u'被预约'),
        (2, u'被借出'),
    )
    state = models.IntegerField(choices=state_choices)


class ActiveRecord(models.Model):
    # user id
    uid = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE)
    # book instance id
    bid = models.ForeignKey(to=BookInstance, on_delete=models.CASCADE)

    active_choices = (
        (0, u'预约'),
        (1, u'借阅'),
        (2, u'归还')
    )
    active = models.IntegerField(choices=active_choices)

    active_time = models.DateTimeField(auto_now_add=True)


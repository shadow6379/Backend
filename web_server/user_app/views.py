import json

from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.contrib.auth import login as login_confirm
from django.contrib.auth import logout as logout_confirm
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required

from user_app import models
from django.db.models import Q
from user_app.emailToken import token_confirm
from django.core.mail import send_mail
from web_server.settings import EMAIL_HOST_USER


from django.views import View
# the website
DOMAIN = 'http://172.18.158.55:8000'
# Create your views here.


def registry(request):
    # args
    email = request.POST.get('email')
    username = request.POST.get('username')
    password = request.POST.get('password')

    result = {
        'status': '',  # 'success' or 'failure'
        'error_msg': '',  # notes of failure
    }

    # if the username or email has existed, register failed
    # if the email is not active, the inactive User will be delete
    model_user = models.User.objects.filter(username=username)
    if model_user:
        result['status'] = 'failure'
        result['error_msg'] = 'the username or the email has exist.'
        return HttpResponse(json.dumps(result))
    model_user = models.User.objects.filter(email=email)
    if model_user:
        # if the email is inactive
        if not model_user[0].is_active:
            model_user[0].delete()
        else:
            result['status'] = 'failure'
            result['error_msg'] = 'the username or the email has exist.'
            return HttpResponse(json.dumps(result))
    user = models.User.objects.create(
        username=username,
        password=password,
        email=email,
        is_active=False
    )
    user.set_password(password)
    user.save()
    token = token_confirm.generate_validate_token(username)
    message = "\n".join([
        u'Hi,{0},welcome to register our system.'.format(username),
        u'Please click the link to confirm your Account:',
        '/'.join([DOMAIN, 'user_app/activate', token]),
        u'If it is not a link form, please copy it to the address bar of your browser and then visit it.'
    ])
    send_mail(u'Email Verification', message, EMAIL_HOST_USER, [email], fail_silently = False)
    result['status'] = 'success'
    return HttpResponse(json.dumps(result))


def active_user(request, token):
    result = {
        'status': '', # 'success' or 'failure'
        'error_msg': '',
    }
    try:
        username = token_confirm.confirm_validate_token(token)
    except:
        username = token_confirm.remove_validate_token(token)
        users = models.User.objects.filter(username=username)
        for user in users:
            user.delete()
        result['status'] = 'failure'
        result['error_msg'] = 'exceed the time limit'
        return HttpResponse(json.dumps(result))
        #return render(request, 'message.html', {'message': u'对不起，验证链接已经过期，请重新<a href=\"' + unicode(django_settings.DOMAIN) + u'/signup\">注册</a>'})
    try:
        user = models.User.objects.get(username=username)
    except models.User.DoesNotExist:
        result['status'] = 'failure'
        result['error_msg'] = 'The user does not exist'
        return HttpResponse(json.dumps(result))
        #return render(request, 'message.html', {'message': u"对不起，您所验证的用户不存在，请重新注册"})
    user.is_active = True
    user.save()
    try:
        userinfo = models.UserInfo.objects.get(user=user)
    except models.UserInfo.DoesNotExist:
        userinfo = models.UserInfo.objects.create(user=user)
        result['status'] = 'success'
        return HttpResponse(json.dumps(result))
    result['status'] = 'failure'
    result['error_msg'] = 'You had verified this account'
    return  HttpResponse(json.dumps(result))


def login(request):
    pass


def logout(request):
    pass


def category(request, cid, begin, end):
    pass


def detail(request, bid):
    pass


def collect_book(request):
    pass


def subscribe_book(request):
    pass


def star_book(request):
    pass


class CommentSection(View):
    # add auth decorator here
    def dispatch(self, request, *args, **kwargs):
        return super(CommentSection, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        pass


class UserProfile(View):
    # add auth decorator here
    def dispatch(self, request, *args, **kwargs):
        return super(UserProfile, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        pass


def retrieve(request):
    pass

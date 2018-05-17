import json

from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views import View
from django.contrib.auth import login as login_confirm
from django.contrib.auth import logout as logout_confirm
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required

from user_app import models
from django.db.models import Q
from user_app.email_token import token_confirm
from django.core.mail import send_mail
from web_server.settings import EMAIL_HOST_USER, DOMAIN
from user_app.utils.method_test import is_post
from user_app.utils.method_test import is_get
from user_app.utils.db_to_dict import process_book_obj
# the website

# Create your views here.


# deal with the register
# return the status, success or failure
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

    '''
    determine the username is exist or not
    if exist, register failed
    if not, determine the email is exist or not
        if exist, determine the user is active or not
            if the user is active, register failed
            if not, delete the user, do something the same as the user didn't exist
        if not, create an instance of User and send a email containing a token verification
    '''
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
    # create in instance of User, set the is_active attribute to False
    user = models.User.objects.create(
        username=username,
        password=password,
        email=email,
        is_active=False
    )
    # encrypt the password, using pbkdf2_sha256 algorithm
    user.set_password(password)
    user.save()
    # create the token
    token = token_confirm.generate_validate_token(username)
    # define the contains of email
    # now the contains are text form, not html form
    message = "\n".join([
        u'Hi,{0},welcome to register our system.'.format(username),
        u'Please click the link to confirm your Account:',
        '/'.join([DOMAIN, 'user_app/activate', token]),
        u'If it is not a link form, please copy it to the address bar of your browser and then visit it.'
    ])
    send_mail(u'Email Verification', message, EMAIL_HOST_USER, [email], fail_silently=False)
    result['status'] = 'success'
    return HttpResponse(json.dumps(result))


# active the user
# return the status, success or failure
def active_user(request, token):
    result = {
        'status': '',     # 'success' or 'failure'
        'error_msg': '',  # notes of failure
    }
    # verify the token
    try:
        username = token_confirm.confirm_validate_token(token)
    except:
        # if the token is exceed the time limit
        # delete the user, and return the failure message
        username = token_confirm.remove_validate_token(token)
        users = models.User.objects.filter(username=username)
        for user in users:
            user.delete()
        result['status'] = 'failure'
        result['error_msg'] = 'exceed the time limit'
        return HttpResponse(json.dumps(result))

    try:
        user = models.User.objects.get(username=username)
    # if the user doesn't exist
    except models.User.DoesNotExist:
        result['status'] = 'failure'
        result['error_msg'] = 'The user does not exist'
        return HttpResponse(json.dumps(result))
    user.is_active = True
    user.save()

    # after active the user
    # create an instance of UserInfo

    # if the userinfo had existed, return the failure message
    try:
        userinfo = models.UserInfo.objects.get(user=user)
    except models.UserInfo.DoesNotExist:
        # create userinfo and return the successful message
        userinfo = models.UserInfo.objects.create(user=user)
        result['status'] = 'success'
        return HttpResponse(json.dumps(result))
    result['status'] = 'failure'
    result['error_msg'] = 'You had verified this account'
    return HttpResponse(json.dumps(result))


def login(request):
    """
    :param request:
    request.POST.get('username')
    request.POST.get('password')
    :return:
    HttpResponse(json.dumps(result))
    """
    result = {
        'status': '',  # 'success' or 'failure'
        'error_msg': '',  # notes of failure
    }

    # handle wrong method
    if not is_post(request, result):
        return HttpResponse(json.dumps(result))

    print(request.POST.get('username'),request.POST.get('password'))

    user = authenticate(
        username=request.POST.get('username'),
        password=request.POST.get('password'),
    )

    if user is not None:
        # pass authentication
        result['status'] = 'success'
        login_confirm(request, user)
        return HttpResponse(json.dumps(result))
    else:
        result['status'] = 'failure'
        result['error_msg'] = 'this user does not exist, or the password is wrong'
        return HttpResponse(json.dumps(result))


@login_required
def logout(request):
    """
    :param request:
    :return:
    HttpResponse(json.dumps(result))
    """
    result = {
        'status': '',  # 'success' or 'failure'
        'error_msg': '',  # notes of failure
    }

    # handle wrong method
    if not is_post(request, result):
        return HttpResponse(json.dumps(result))

    logout_confirm(request)
    result['status'] = 'success'
    return HttpResponse(json.dumps(result))


def category(request, cid, begin, end):
    """
    :param request:
    :param cid: book type's id
    :param begin: [begin, end)
    :param end:
    :return:
    HttpResponse(json.dumps(result))
    """
    result = {
        'status': '',  # 'success' or 'failure'
        'msg': '',
        'error_msg': '',  # notes of failure
    }

    # handle wrong method
    if not is_get(request, result):
        return HttpResponse(json.dumps(result))

    book_type = models.TypeInfo.objects.filter(id=cid).first()

    if book_type is None:
        result['status'] = 'failure'
        result['error_msg'] = 'invalid category id'
        return HttpResponse(json.dumps(result))

    # get all related db obj
    related_books = book_type.related_books.all()

    # use dict to store db obj (id-info)
    book_dict = dict()
    for i in range(related_books.count()):
        if i < int(begin):
            continue
        elif i >= int(end):
            break

        # transfer db obj to dict
        book = process_book_obj(related_books[i])

        book_dict[str(related_books[i].id)] = json.dumps(book)

    result['status'] = "success"
    result['msg'] = json.dumps(book_dict)

    return HttpResponse(json.dumps(result))


def detail(request, bid):
    """
    :param request:
    :param bid: book id
    :return:

    HttpResponse(json.dumps(result))
    """
    result = {
        'status': '',  # 'success' or 'failure'
        'msg': '',
        'error_msg': '',  # notes of failure
    }
    pass


@login_required
def collect_book(request):
    pass


@login_required
def subscribe_book(request):
    pass


@login_required
def star_book(request):
    pass


class CommentSection(View):
    @staticmethod
    def get(request):
        pass

    @staticmethod
    @login_required
    def post(request):
        pass


class UserProfile(View):
    @login_required
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


# handle error request (wrong url)
def error_handle(request):
    return HttpResponse(json.dumps({'status': 'failure'}))

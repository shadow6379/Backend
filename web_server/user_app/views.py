import json

from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views import View
from django.contrib.auth import login as login_confirm
from django.contrib.auth import logout as logout_confirm
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import utils
from django.db import transaction

from user_app import models
from user_app.email_token import token_confirm
from django.core.mail import send_mail
from web_server.settings import EMAIL_HOST_USER, DOMAIN, DEBUG
from user_app.utils.method_test import is_post
from user_app.utils.method_test import is_get
from user_app.utils.db_to_dict import process_book_obj, process_user_obj, comment_to_dict
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
    # if the email is+ not active, the inactive User will be delete

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
    """  The book detail information

    :param request:
    :param bid: book id
    :return:

    HttpResponse(json.dumps(result))
    """
    result = {
        'status': '',  # 'success' or 'failure'
        'msg': '',  # msg of the book
        'error_msg': '',  # notes of failure
    }
    # the error method
    if not is_get(request, result):
        return HttpResponse(json.dumps(result))

    # filter the list of book
    # actually, the number of book is 0 or 1
    books = models.BookInfo.objects.filter(id=bid).first()

    # if the number of book is 0
    if books is None:
        result['status'] = 'failure'
        result['error_msg'] = 'invalid book id'
        return HttpResponse(json.dumps(result))

    book_dict = dict()
    # transfer db obj to dict
    book = process_book_obj(books)
    book_dict[str(books.id)] = json.dumps(book)

    result['status'] = "success"
    result['msg'] = json.dumps(book_dict)

    return HttpResponse(json.dumps(result))


@login_required
def collect_book(request):
    """
    :param request:
    request.POST.get('bid'): book id
    request.user.id: user id
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

    book = models.BookInfo.objects.filter(id=int(request.POST.get('bid'))).first()

    # book not exist
    if book is None:
        result['status'] = 'failure'
        result['error_msg'] = 'invalid book id'
        return HttpResponse(json.dumps(result))

    user = models.UserInfo.objects.filter(id=int(request.user.id)).first()
    # add the book to user's collections
    user.collections.add(int(request.POST.get('bid')))
    result['status'] = 'success'

    return HttpResponse(json.dumps(result))


@login_required
def subscribe_book(request):
    """
    :param request:
    request.POST.get('bid')
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

    book_id = request.POST.get('bid')
    # if doesn't contain the book's id
    if not book_id:
        result['status'] = 'failure'
        result['error_msg'] = "must offer the book's id"
        return HttpResponse(json.dumps(result))
    # if the book doesn't exist
    book = models.BookInfo.objects.filter(id=int(book_id))
    if not book:
        result['status'] = 'failure'
        result['error_msg'] = "the book doesn't exist"
        return HttpResponse(json.dumps(result))

    book = book[0]
    user = models.UserInfo.objects.get(user=request.user)
    book_state = models.BookInstance.objects.filter(bid=book)
    with transaction.atomic():
        # if not exist
        if not book_state:
            # print("not book_state")
            book_state = models.BookInstance.objects.create(
                bid=book,
                state=1,
            )
            models.ActiveRecord.objects.create(
                uid=user,
                bid=book_state,
                active=0,
            )
            result['status'] = 'success'
            return HttpResponse(json.dumps(result))
        # if the book's state is not normal
        elif book_state[0].state != 0:
            # print("book_state not equal 0")
            result['status'] = 'failure'
            result['error_msg'] = "the book has been subscribed or borrowed"
            return HttpResponse(json.dumps(result))
        elif book_state[0].state == 0:
            # print("book_state equal 0")
            book_state[0].state = 1,
            book_state[0].save()
            models.ActiveRecord.objects.create(
                uid=user,
                bid=book_state[0],
                active=0,
            )
            result['status'] = 'success'
            return HttpResponse(json.dumps(result))


@login_required
def star_book(request):
    """
    :param request:
    request.POST.get('bid')
    request.POST.get('star')
    :return:
    HttpResponse(json.dumps(result))
    """
    result = {
        'status': '',  # 'success' or 'failure'
        'error_msg': '',  # notes of failure
    }
    # get the book's id and the score to the book
    book_id = int(request.POST.get('bid'))
    star = int(request.POST.get('star'))
    # if the score not in [1, 5], return failure
    if star < 1 or star > 5:
        result['status'] = 'failure'
        result['error_msg'] = 'Score out of field'
        return HttpResponse(json.dumps(result))
    # user_info = models.UserInfo.objects.get(user=request.user)
    # book_info = models.UserInfo.objects.get(id=book_id)
    try:
        score_to_book = models.ScoreToBook.objects.create(
            uid_id=request.user.id,
            bid_id=book_id,
            score=star,
        )
    # if you have starred the book, return failure
    except utils.IntegrityError:
        result['status'] = 'failure'
        result['error_msg'] = 'You have starred'
        return HttpResponse(json.dumps(result))
    '''
    book = models.BookInfo.objects.get(id=book_id)
    book.score = star
    book.save()
    '''
    result['status'] = 'success'
    return HttpResponse(json.dumps(result))


class CommentSection(View):
    @staticmethod
    def get(request, bid):
        """
        :param request:
        :param bid: book's id
        :return:
        HttpResponse(json.dumps(result))
        """
        print("get")
        result = {
            'status': '',  # 'success' or 'failure'
            'msg': '',  # information of the comment section
            'error_msg': '',  # notes of failure
        }
        # get all the comment on this book
        comment = dict()
        comment_all = models.Comment.objects.filter(bid_id=int(bid)).order_by('comment_time')
        # print(comment_all)
        # print(comment_all.count())
        # the comment represented like comments in weibo
        for i in range(comment_all.count()):
            parent_id = comment_all[i].parent_comment_id
            if parent_id == 0:
                temp = dict()
                temp[comment_all[i].id] = comment_to_dict(comment_all[i])
                comment[comment_all[i].id] = temp
            else:
                if comment.get(parent_id):
                    comment[parent_id][comment_all[i].id] = comment_to_dict(comment_all[i])
                else:
                    for comment_temp in comment:
                        if comment_temp.get(parent_id):
                            comment_temp[parent_id] = comment_to_dict(comment_all[i])

        result['msg'] = json.dumps(comment)
        result['status'] = 'success'
        return HttpResponse(json.dumps(result))

    @staticmethod
    @login_required
    def post(request, bid):
        """
        :param request:
        :param bid: book's id
        :return:
        HttpResponse(json.dumps(result))
        """
        result = {
            'status': '',  # 'success' or 'failure'
            'error_msg': '',  # notes of failure
        }
        protocol = request.POST.get('protocol')
        msg = request.POST.get('msg')
        parent = request.POST.get('parent')
        # get the user
        user = models.UserInfo.objects.get(user=request.user)

        # if protocol is 0, represent comment
        # you can comment a book more than one time
        if protocol == '0':
            comment = models.Comment.objects.create(
                uid=user,
                bid_id=int(bid),
                content=msg,
                parent_comment_id=int(parent),
            )
            result['status'] = 'success'
            return HttpResponse(json.dumps(result))
        # if protocol is 1, represent agree
        # if protocol is 2, represent disagree
        # You can only do this once.
        elif protocol == '1' or protocol == '2':
            comment = models.Comment.objects.get(id=int(parent))
            try:
                models.AttitudeRecord.objects.create(
                    cid=comment,
                    uid_id=bid,
                    attitude=int(protocol)-1,
                )
                result['status'] = 'success'
            except utils.IntegrityError:
                result['status'] = 'failure'
                result['error_msg'] = 'You have give your attitude on this comment'
            finally:
                return HttpResponse(json.dumps(result))
        # if protocol is 3, represent report
        # You can only do this once.
        elif protocol == '3':
            comment = models.Comment.objects.get(id=int(parent))
            try:
                models.AttitudeRecord.objects.create(
                    cid=comment,
                    bid_id=bid,
                    attitude=int(protocol)-1,
                    report_reason = int(request.POST.get('reason'))
                )
                result['status'] = 'success'
            except utils.IntegrityError:
                result['status'] = 'failure'
                result['error_msg'] = 'You have already reported it.'
            finally:
                return HttpResponse(json.dumps(result))


class UserProfile(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserProfile, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request, uid):
        result = {
            'status': '',
            'msg': '',
            'error_msg': '',
        }
        user = models.User.objects.filter(id=uid)
        if not user:
            result['status'] = 'failure'
            result['error_msg'] = "user doesn't not existed"
            return HttpResponse(json.dumps(result))

        # user_dict = dict()
        # transfer db obj to dict
        user_info = process_user_obj(user[0])
        # print(user_info)
        result['status'] = "success"
        result['msg'] = json.dumps(user_info)

        return HttpResponse(json.dumps(result))

    @staticmethod
    def post(request, uid):
        result = {
            'status': '',
            'error_msg': '',
        }
        user = models.User.objects.filter(id=uid)
        # actually, this situation can not happen
        if not user:
            result['status'] = 'failure'
            result['error_msg'] = "user doesn't not existed"
            return HttpResponse(json.dumps(result))

        user = user[0]
        user_info = models.UserInfo.objects.filter(user=user)

        # actually, this situation can not happen
        if not user_info:
            result['status'] = 'success'
            return HttpResponse(json.dumps(result))

        # the information user can change are the 'other'
        # the other information can't change
        user_info = user_info[0]

        # change the password
        if request.POST.get('old_password'):
            user = authenticate(
                username=request.user.username,
                password=request.POST.get('old_password'),
            )
            # if the old password is wrong
            if not user:
                result['status'] = 'failure'
                result['error_msg'] = 'error password, please enter the correct password'
                return HttpResponse(json.dumps(result))

            # change password
            user.set_password(request.POST.get('new_password'))
            user.save()

        if request.POST.get('other'):
            user_info.gender = request.POST.get('other')

        result['status'] = 'success'

        return HttpResponse(json.dumps(result))


# search books
def retrieve(request):
    """  Searching books by

        :param request:
        :return:
        HttpResponse(json.dumps(result))

    """
    result = {
        'status': '',  # 'success' or 'failure'
        'msg': '',  # information of the retrieve
        'error_msg': '',  # notes of failure
    }

    book_dict = {} # a dictionary stored the search results

    # get the Key word
    search_name = request.GET.get('key')
    if not search_name:
        result['status'] = 'failure'
        result['error_msg'] = 'please offer the key word'
        return HttpResponse(json.dumps(result))
    # assume the Key word is book's name
    books_by_name = models.BookInfo.objects.filter(name__icontains=search_name)
    # assume the Key word is book's author
    books_by_author = models.BookInfo.objects.filter(author__icontains=search_name)

    # print the search results
    if DEBUG:
        print("search books by name: %s" % books_by_name)
        print("search books by author: %s" % books_by_author)

    # if find nothing, the status become false
    if not books_by_name and not books_by_author:
        result['status'] = "failed"
        result['error_msg'] = "We can't find what you want, please try again."

        return HttpResponse(json.dumps(result))

    # get all the books through books_by_name
    for i in range(books_by_name.count()):
        book = process_book_obj(books_by_name[i])
        book_dict[str(books_by_name[i].id)] = json.dumps(book)
    # get all the books through books_by_author
    for i in range(books_by_author.count()):
        # if the book is not in the book_dict
        if str(books_by_author[i].id) not in book_dict:
            book = process_book_obj(books_by_author[i])
            book_dict[str(books_by_author[i].id)] = json.dumps(book)

    result['status'] = "success"
    result['msg'] = json.dumps(book_dict)

    return HttpResponse(json.dumps(result))


# handle error request (wrong url)
def error_handle(request):
    return HttpResponse(json.dumps({'status': 'failure'}))

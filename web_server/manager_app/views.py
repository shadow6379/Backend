import json

from django.shortcuts import HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.db import transaction

from manager_app import models
from user_app import models as tmp    # optimization: message queue
from manager_app.utils.mgr_auth import SALT
from manager_app.utils.mgr_auth import authenticate
from manager_app.utils.method_test import is_post
from manager_app.utils.method_test import is_get
from manager_app.utils.db_to_dict import process_mgr_obj
from manager_app.utils.db_to_dict import process_record_obj
from manager_app.utils.db_to_dict import process_book_obj

# Create your views here.


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

    username = request.POST.get('username')
    password = request.POST.get('password')

    mgr = models.ManagerInfo.objects.filter(
        username=username,
        password=password,
    )

    if mgr.count() == 1:
        result['status'] = 'success'
        response = HttpResponse(json.dumps(result))
        response.set_signed_cookie(key='username', value=username, salt=SALT)
        return response
    else:
        result['status'] = 'failure'
        result['error_msg'] = 'this user does not exist, or the password is wrong'
        return HttpResponse(json.dumps(result))


@authenticate
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

    result['status'] = 'success'
    response = HttpResponse(json.dumps(result))
    response.delete_cookie(key='username')

    return response


@authenticate
def manager_info(request):
    """
    :param request:
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

    username = request.get_signed_cookie(key='username', salt=SALT)
    mgr = models.ManagerInfo.objects.filter(username=username).first()

    if mgr:
        result['status'] = 'success'
        mgr_dict = process_mgr_obj(mgr)
        result['msg'] = json.dumps(mgr_dict)
    else:
        result['status'] = 'failure'
        result['error_msg'] = 'mgr db info may be deleted'

    return HttpResponse(json.dumps(result))


class ReportInfoBox(View):
    @method_decorator(authenticate)
    def dispatch(self, request, *args, **kwargs):
        return super(ReportInfoBox, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        """
        :param request:
        :return:
        HttpResponse(json.dumps(result))
        """
        result = {
            'status': '',  # 'success' or 'failure'
            'msg': '',
            'error_msg': '',  # notes of failure
        }

        reports = tmp.AttitudeRecord.objects.filter(attitude=2)
        report_dict = dict()
        for i in range(reports.count()):
            report_reason = str(reports[i].report_reason)
            cid = str(reports[i].cid.id)

            # add an item for a new comment
            if cid not in report_dict.keys():
                # detail report reason info is in db
                report_dict[cid] = {
                    'content': reports[i].cid.content,
                    'report_reasons': {
                        '0': '0',
                        '1': '0',
                        '2': '0',
                        '3': '0',
                        '4': '0',
                        '5': '0',
                        '6': '0',
                        '7': '0',
                        '8': '0',
                    },
                }

            # keep using str
            report_dict[cid]['report_reasons'][report_reason] = \
                str(int(report_dict[cid]['report_reasons'][report_reason]) + 1)

        # stringify data
        for key in report_dict.keys():
            report_dict[key]['report_reasons'] = \
                json.dumps(report_dict[key]['report_reasons'])
            report_dict[key] = json.dumps(report_dict[key])
        result['msg'] = json.dumps(report_dict)
        result['status'] = 'success'

        return HttpResponse(json.dumps(result))

    @staticmethod
    def post(request):
        """
        :param request:
        request.POST.get('protocol'): '0' means delete comment,
                                    '1' means delete related report
        request.POST.get('cid'): target comment id
        :return:
        HttpResponse(json.dumps(result))
        """
        result = {
            'status': '',  # 'success' or 'failure'
            'error_msg': '',  # notes of failure
        }

        protocol = request.POST.get('protocol')
        if protocol is None:
            result['status'] = 'failure'
            result['error_msg'] = 'protocol required'
            return HttpResponse(json.dumps(result))

        cid = request.POST.get('cid')
        if cid is None:
            result['status'] = 'failure'
            result['error_msg'] = 'cid (comment id) required'
            return HttpResponse(json.dumps(result))

        if protocol == '0':
            # delete comment
            tmp.Comment.objects.filter(id=cid).delete()
            result['status'] = 'success'
        elif protocol == '1':
            # delete related reports
            tmp.AttitudeRecord.objects.filter(cid=cid).delete()
            result['status'] = 'success'
        else:
            result['status'] = 'failure'
            result['error_msg'] = 'invalid protocol'

        return HttpResponse(json.dumps(result))


class TypeManagement(View):
    @method_decorator(authenticate)
    def dispatch(self, request, *args, **kwargs):
        return super(TypeManagement, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        """
        :param request:
        :return:
        HttpResponse(json.dumps(result))
        """
        result = {
            'status': '',  # 'success' or 'failure'
            'msg': '',  # information of the type
            'error_msg': '',  # notes of failure
        }

        # get all types
        types = tmp.TypeInfo.objects.all()

        # change db obj into dict
        type_dict = dict()
        for i in range(types.count()):
            type_dict[str(types[i].id)] = types[i].name
        result['msg'] = json.dumps(type_dict)
        result['status'] = 'success'

        return HttpResponse(json.dumps(result))

    @staticmethod
    def post(request):
        """
        :param request:
        :param request:
        request.POST.get('protocol'): '0' means add type,
                                    '1' means delete type,
                                    '2' means update type,
        request.POST.get('old')
        request.POST.get('new')
        :return:
        HttpResponse(json.dumps(result))
        """
        result = {
            'status': '',  # 'success' or 'failure'
            'error_msg': '',  # notes of failure
        }

        protocol = request.POST.get('protocol')
        if protocol is None:
            result['status'] = 'failure'
            result['error_msg'] = 'protocol required'
            return HttpResponse(json.dumps(result))

        if protocol == '0':
            new = request.POST.get('new')
            if new is None:
                result['status'] = 'failure'
                result['error_msg'] = 'new required'
                return HttpResponse(json.dumps(result))

            try:
                tmp.TypeInfo.objects.create(name=new)
            except:
                result['status'] = 'failure'
                result['error_msg'] = 'this type is already in the db'
                return HttpResponse(json.dumps(result))
        elif protocol == '1':
            old = request.POST.get('old')
            if old is None:
                result['status'] = 'failure'
                result['error_msg'] = 'old required'
                return HttpResponse(json.dumps(result))
            target = tmp.TypeInfo.objects.filter(name=old)

            # old type is not exist in the db
            if target.count() == 0:
                result['status'] = 'failure'
                result['error_msg'] = 'invalid type'
                return HttpResponse(json.dumps(result))
            target.delete()
        elif protocol == '2':
            new = request.POST.get('new')
            if new is None:
                result['status'] = 'failure'
                result['error_msg'] = 'new required'
                return HttpResponse(json.dumps(result))

            old = request.POST.get('old')
            if old is None:
                result['status'] = 'failure'
                result['error_msg'] = 'old required'
                return HttpResponse(json.dumps(result))

            target = tmp.TypeInfo.objects.filter(name=old)

            # old type is not exist in the db
            if target.count() == 0:
                result['status'] = 'failure'
                result['error_msg'] = 'invalid type'
                return HttpResponse(json.dumps(result))

            try:
                target.update(name=new)
            except:
                result['status'] = 'failure'
                result['error_msg'] = 'this type is already in the db'
                return HttpResponse(json.dumps(result))
        else:
            result['status'] = 'failure'
            result['error_msg'] = 'invalid protocol'
            return HttpResponse(json.dumps(result))
        result['status'] = 'success'

        return HttpResponse(json.dumps(result))


class InventoryManagement(View):
    @method_decorator(authenticate)
    def dispatch(self, request, *args, **kwargs):
        return super(InventoryManagement, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        """retrieve book by keyword
        :param request:
        request.GET.get('key')
        :return:
        HttpResponse(json.dumps(result))
        """
        result = {
            'status': '',  # 'success' or 'failure'
            'msg': '',  # information of the retrieve
            'error_msg': '',  # notes of failure
        }

        key = request.GET.get('key')

        if key is None:
            result['status'] = 'failure'
            result['error_msg'] = 'key required'
            return HttpResponse(json.dumps(result))

        # keyword is ISBN
        book_by_ISBN = tmp.BookInfo.objects.filter(ISBN=key).first()
        if book_by_ISBN is not None:
            book_dict = dict()
            book = process_book_obj(book_by_ISBN)
            book_dict[str(book_by_ISBN.id)] = json.dumps(book)
            result['msg'] = json.dumps(book_dict)
            result['status'] = "success"
            return HttpResponse(json.dumps(result))

        # keyword in book name
        books_by_name = tmp.BookInfo.objects.filter(name__icontains=key)
        # keyword in author name
        books_by_author = tmp.BookInfo.objects.filter(author__icontains=key)

        book_dict = dict()
        # process books_by_name
        for i in range(books_by_name.count()):
            book = process_book_obj(books_by_name[i])
            book_dict[str(books_by_name[i].id)] = json.dumps(book)
        # process books_by_author
        for i in range(books_by_author.count()):
            # ensure the book is not in the book_dict
            if str(books_by_author[i].id) not in book_dict.keys():
                book = process_book_obj(books_by_author[i])
                book_dict[str(books_by_author[i].id)] = json.dumps(book)
        result['msg'] = json.dumps(book_dict)
        result['status'] = "success"

        return HttpResponse(json.dumps(result))

    @staticmethod
    def post(request):
        """
        :param request:
        request.POST.get('protocol'): '0' means add item,
                                    '1' means update item
        request.POST.get('msg')
        :return:
        HttpResponse(json.dumps(result))
        """
        result = {
            'status': '',  # 'success' or 'failure'
            'error_msg': '',  # notes of failure
        }

        protocol = request.POST.get('protocol')
        if protocol is None:
            result['status'] = 'failure'
            result['error_msg'] = 'protocol required'
            return HttpResponse(json.dumps(result))

        msg = request.POST.get('msg')
        if msg is None:
            result['status'] = 'failure'
            result['error_msg'] = 'msg required'
            return HttpResponse(json.dumps(result))

        msg = json.loads(msg)
        msg['types'] = json.loads(msg['types'])

        if protocol == '0':
            obj = tmp.BookInfo.objects.filter(ISBN=msg['ISBN']).first()

            if obj is not None:
                result['status'] = 'failure'
                result['error_msg'] = 'ISBN is not unique'
                return HttpResponse(json.dumps(result))

            types = []
            for v in msg['types'].values():
                t = tmp.TypeInfo.objects.filter(name=v).first()

                # ensure book type is valid
                if t is None:
                    result['status'] = 'failure'
                    result['error_msg'] = 'invalid book type'
                    return HttpResponse(json.dumps(result))
                types.append(t.id)

            # start a transaction
            with transaction.atomic():
                # create book obj
                book = tmp.BookInfo(
                    cover=msg['cover'],
                    name=msg['name'],
                    author=msg['author'],
                    brief=msg['brief'],
                    ISBN=msg['ISBN'],
                    publish_time=msg['publish_time'],
                    press=msg['press'],
                    contents=msg['contents'],
                )
                book.save()
                book.types.set(types)
                book.save()

                # create book instance
                for i in range(int(msg['inventory'])):
                    tmp.BookInstance.objects.create(
                        bid=book,
                        state=0,
                    )
        elif protocol == '1':
            book = tmp.BookInfo.objects.filter(ISBN=msg['ISBN']).first()

            # ensure book exist
            if book is None:
                result['status'] = 'failure'
                result['error_msg'] = 'book identified by ISBN is not in the DB'
                return HttpResponse(json.dumps(result))

            # book instance can not be deleted
            count = book.book_instances.filter(state=0).count()
            if count > int(msg['inventory']):
                result['status'] = 'failure'
                result['error_msg'] = 'can not delete book instance'
                return HttpResponse(json.dumps(result))

            types = []
            for v in msg['types'].values():
                t = tmp.TypeInfo.objects.filter(name=v).first()

                # ensure book type is valid
                if t is None:
                    result['status'] = 'failure'
                    result['error_msg'] = 'invalid book type'
                    return HttpResponse(json.dumps(result))
                types.append(t.id)

            # start a transaction
            with transaction.atomic():
                book.cover = msg['cover']
                book.name = msg['name']
                book.author = msg['author']
                book.brief = msg['brief']
                book.publish_time = msg['publish_time']
                book.press = msg['press']
                book.contents = msg['contents']
                book.types.set(types)
                book.save()

                # create book instance
                for i in range(int(msg['inventory']) - count):
                    tmp.BookInstance.objects.create(
                        bid=book,
                        state=0,
                    )
        else:
            result['status'] = 'failure'
            result['error_msg'] = 'invalid protocol'
            return HttpResponse(json.dumps(result))
        result['status'] = 'success'

        return HttpResponse(json.dumps(result))


class Debit(View):
    @method_decorator(authenticate)
    def dispatch(self, request, *args, **kwargs):
        return super(Debit, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        """get user's order record
        :param request:
        request.GET.get('username')
        :return:
        HttpResponse(json.dumps(result))
        """
        result = {
            'status': '',  # 'success' or 'failure'
            'msg': '',  # the selected user's all debit record
            'error_msg': '',  # notes of failure
        }

        # ensure request contains 'username'
        username = request.GET.get('username')
        if username is None:
            result['status'] = 'failure'
            result['error_msg'] = 'username required'
            return HttpResponse(json.dumps(result))

        # ensure related user is in db
        user = tmp.UserInfo.objects.filter(user__username=username).first()
        if user is None:
            result['status'] = 'failure'
            result['error_msg'] = 'related user not exists'
            return HttpResponse(json.dumps(result))

        # process data
        records = tmp.ActiveRecord.objects.filter(uid=user.id).filter(active=0)
        record_dict = {}
        for i in range(records.count()):
            record = process_record_obj(records[i])
            record_dict[str(records[i].id)] = json.dumps(record)
        result['msg'] = json.dumps(record_dict)
        result['status'] = 'success'

        return HttpResponse(json.dumps(result))

    @staticmethod
    def post(request):
        """
        :param request:
        request.POST.get('msg')
        :return:
        HttpResponse(json.dumps(result))
        """
        result = {
            'status': '',  # 'success' or 'failure'
            'error_msg': '',  # notes of failure
        }

        # ensure request contains 'msg'
        msg = request.POST.get('msg')
        if msg is None:
            result['status'] = 'failure'
            result['error_msg'] = 'msg (debit message) required'
            return HttpResponse(json.dumps(result))

        msg = json.loads(msg)

        # ensure msg contains 'username' and 'bid'
        if 'username' not in msg.keys() or 'bid' not in msg.keys():
            result['status'] = 'failure'
            result['error_msg'] = 'msg must contain username and bid'
            return HttpResponse(json.dumps(result))

        # ensure user exists
        user = tmp.UserInfo.objects.filter(user__username=msg['username']).first()
        if user is None:
            result['status'] = 'failure'
            result['error_msg'] = 'related user not exists'
            return HttpResponse(json.dumps(result))

        # ensure book exists
        book = tmp.BookInfo.objects.filter(id=int(msg['bid'])).first()
        if book is None:
            result['status'] = 'failure'
            result['error_msg'] = 'the desired book not exists'
            return HttpResponse(json.dumps(result))

        # start a transaction
        with transaction.atomic():
            # get the book instance
            book_instance = book.book_instances.filter(state=1).first()
            if book_instance:
                book_instance.state = 2
                book_instance.save()
                tmp.ActiveRecord.objects.get(
                    uid=user,
                    bid=book_instance,
                    active=0,
                ).delete()
                # record debit
                tmp.ActiveRecord.objects.create(
                    uid=user,
                    bid=book_instance,
                    active=1,
                )
            elif book_instance is None:
                book_instance_new = book.book_instances.filter(state=0).first()
                if book_instance_new is None:
                    result['status'] = 'failure'
                    result['error_msg'] = 'inadequate inventory'
                    return HttpResponse(json.dumps(result))
                book_instance_new.state = 2
                book_instance_new.save()
                tmp.ActiveRecord.objects.create(
                    uid=user,
                    bid=book_instance_new,
                    active=1,
                )

        result['status'] = 'success'

        return HttpResponse(json.dumps(result))


class Return(View):
    @method_decorator(authenticate)
    def dispatch(self, request, *args, **kwargs):
        return super(Return, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        """get user's debit record
        :param request:
        request.GET.get('username')
        :return:
        HttpResponse(json.dumps(result))
        """
        result = {
            'status': '',  # 'success' or 'failure'
            'msg': '',    # the selected user's all debit record
            'error_msg': '',  # notes of failure
        }

        # ensure request contains 'username'
        username = request.GET.get('username')
        if username is None:
            result['status'] = 'failure'
            result['error_msg'] = 'username required'
            return HttpResponse(json.dumps(result))

        # ensure related user is in db
        user = tmp.UserInfo.objects.filter(user__username=username).first()
        if user is None:
            result['status'] = 'failure'
            result['error_msg'] = 'related user not exists'
            return HttpResponse(json.dumps(result))

        # process data
        records = tmp.ActiveRecord.objects.filter(uid=user.id).filter(active=1)
        record_dict = {}
        for i in range(records.count()):
            record = process_record_obj(records[i])
            record_dict[str(records[i].id)] = json.dumps(record)
        result['msg'] = json.dumps(record_dict)
        result['status'] = 'success'

        return HttpResponse(json.dumps(result))

    @staticmethod
    def post(request):
        """
        :param request:
        request.POST.get('rid'):
        :return:
        HttpResponse(json.dumps(result))
        """
        result = {
            'status': '',  # 'success' or 'failure'
            'error_msg': '',  # notes of failure
        }

        # ensure request contains 'rid'
        rid = request.POST.get('rid')
        if rid is None:
            result['status'] = 'failure'
            result['error_msg'] = 'rid (record id) required'
            return HttpResponse(json.dumps(result))
        rid = int(rid)

        # ensure related active record is in db
        record = tmp.ActiveRecord.objects.filter(id=rid).first()
        if record is None:
            result['status'] = 'failure'
            result['error_msg'] = 'related active record not exists'
            return HttpResponse(json.dumps(result))

        # add return record
        tmp.ActiveRecord.objects.create(
            uid=record.uid,
            bid=record.bid,
            active=2,
        )

        # change related book instance's state into common
        record.bid.state = 0
        record.bid.save()

        # delete target active record
        tmp.ActiveRecord.objects.filter(id=rid).delete()
        result['status'] = 'success'

        return HttpResponse(json.dumps(result))


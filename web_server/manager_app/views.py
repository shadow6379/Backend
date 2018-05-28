import json

from django.shortcuts import HttpResponse
from django.views import View
from django.utils.decorators import method_decorator

from manager_app import models
from user_app import models as tmp    # optimization: message queue
from manager_app.utils.mgr_auth import SALT
from manager_app.utils.mgr_auth import authenticate
from manager_app.utils.method_test import is_post
from manager_app.utils.method_test import is_get
from manager_app.utils.db_to_dict import process_mgr_obj
from manager_app.utils.db_to_dict import process_record_obj

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
        pass

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

        cid = request.POST.get('cid')
        if cid is None:
            result['status'] = 'failure'
            result['error_msg'] = 'cid (comment id) required'

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


class InventoryManagement(View):
    @method_decorator(authenticate)
    def dispatch(self, request, *args, **kwargs):
        return super(InventoryManagement, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        pass


class Debit(View):
    @method_decorator(authenticate)
    def dispatch(self, request, *args, **kwargs):
        return super(Debit, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        pass


class Return(View):
    @method_decorator(authenticate)
    def dispatch(self, request, *args, **kwargs):
        return super(Return, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        """
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
        records = tmp.ActiveRecord.objects.filter(uid=user.id)
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

        # ensure related active record is in db
        record = tmp.ActiveRecord.objects.filter(id=rid).first()
        if record is None:
            result['status'] = 'failure'
            result['error_msg'] = 'related active record not exists'
            return HttpResponse(json.dumps(result))

        # delete target active record
        tmp.ActiveRecord.objects.filter(id=rid).delete()
        result['status'] = 'success'

        return HttpResponse(json.dumps(result))


import json

from django.shortcuts import HttpResponse
from django.views import View

from manager_app import models
from manager_app.utils.mgr_auth import SALT
from manager_app.utils.mgr_auth import authenticate
from manager_app.utils.method_test import is_post

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
    pass


@authenticate
def manager_info(request):
    pass


class ReportInfoBox(View):
    @authenticate
    def dispatch(self, request, *args, **kwargs):
        return super(ReportInfoBox, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        pass


class InventoryManagement(View):
    @authenticate
    def dispatch(self, request, *args, **kwargs):
        return super(InventoryManagement, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        pass


class Debit(View):
    @authenticate
    def dispatch(self, request, *args, **kwargs):
        return super(Debit, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        pass


class Return(View):
    @authenticate
    def dispatch(self, request, *args, **kwargs):
        return super(Return, self).dispatch(request, *args, **kwargs)

    @staticmethod
    def get(request):
        pass

    @staticmethod
    def post(request):
        pass


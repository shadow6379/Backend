import json

from django.shortcuts import HttpResponse
from django.views import View

from manager_app import models
from manager_app.local_info import auth_info

# Create your views here.


def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    result = {
        'status': '',
        'error_msg': '',
    }

    mgr = models.ManagerInfo.objects.filter(
        username=username,
        password=password,
    )

    if mgr.count() == 1:
        result['status'] = 'success'
        response = HttpResponse(json.dumps(result))
        response.set_signed_cookie(key='username', value=username, salt=auth_info.SALT)
        return response
    else:
        result['status'] = 'failure'
        result['error_msg'] = 'this user does not exist, or the password is wrong'
        return HttpResponse(json.dumps(result))


def authenticate(func):

    def inner(request, *args, **kwargs):
        result = {
            'status': '',
            'error_msg': '',
        }

        try:
            username = request.get_signed_cookie(key='username', salt=auth_info.SALT)
        except KeyError:
            result['status'] = 'failure'
            result['error_msg'] = 'key error'
            return HttpResponse(json.dumps(result))

        if not username:
            result['status'] = 'failure'
            result['error_msg'] = 'need to be authenticated'
            return HttpResponse(json.dumps(result))

        return func(request, *args, **kwargs)

    return inner


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


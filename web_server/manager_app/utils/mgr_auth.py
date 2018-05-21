import json

from django.shortcuts import HttpResponse

SALT = 'admin123'


def authenticate(func):
    def inner(request, *args, **kwargs):
        result = {
            'status': '',
            'error_msg': '',
        }

        try:
            username = request.get_signed_cookie(key='username', salt=SALT)
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

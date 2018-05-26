def is_get(request, result):
    if request.method != 'GET':
        result['status'] = 'failure'
        result['error_msg'] = 'please use GET method!'
        return False
    else:
        return True


def is_post(request, result):
    if request.method != 'POST':
        result['status'] = 'failure'
        result['error_msg'] = 'please use POST method!'
        return False
    else:
        return True


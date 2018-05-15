def is_post(request, result):
    if request.method != 'POST':
        result['status'] = 'failure'
        result['error_msg'] = 'please use POST method!'
        return False
    else:
        return True


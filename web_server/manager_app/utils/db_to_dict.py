from manager_app import models


def process_mgr_obj(obj):
    mgr = dict()

    mgr['username'] = obj.username
    mgr['email'] = obj.email
    mgr['gender'] = obj.get_gender_display()
    mgr['phone'] = obj.phone
    mgr['other'] = obj.other

    return mgr

from user_app import models as tmp


def process_mgr_obj(obj):
    mgr = dict()

    mgr['username'] = obj.username
    mgr['email'] = obj.email
    mgr['gender'] = obj.get_gender_display()
    mgr['phone'] = obj.phone
    mgr['other'] = obj.other

    return mgr


def process_record_obj(obj):
    record = dict()

    user = tmp.UserInfo.objects.filter(id=obj.uid).first()
    book = tmp.BookInfo.objects.filter(id=obj.bid).first()

    record['username'] = user.user__username
    record['book'] = book.name
    record['active_time'] = str(obj.active_time)

    return record

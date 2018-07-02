import json

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

    user = tmp.UserInfo.objects.filter(id=obj.uid.id).first()
    book = tmp.BookInstance.objects.filter(id=obj.bid.id).first()

    record['username'] = user.user.username
    record['bid'] = book.bid.id
    record['book'] = book.bid.name
    record['active_time'] = str(obj.active_time)

    return record


def process_book_obj(obj):
    book = dict()

    book['cover'] = str(obj.cover)
    book['name'] = obj.name
    book['author'] = obj.author
    book['score'] = str(obj.score)
    book['brief'] = obj.brief
    book['ISBN'] = obj.ISBN
    book['publish_time'] = obj.publish_time
    book['press'] = obj.press
    book['contents'] = obj.contents
    book['inventory'] = str(obj.book_instances.filter(state=0).count())

    type_dict = dict()
    for t in obj.types.all():
        type_dict[str(t.id)] = t.name
    book['types'] = json.dumps(type_dict)

    return book


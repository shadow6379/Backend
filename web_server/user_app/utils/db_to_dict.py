import json
from user_app import models


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


def process_user_obj(obj):
    user = dict()

    user['username'] = obj.username
    user['email'] = obj.email

    user_info = models.UserInfo.objects.filter(user=obj)
    if not user_info:
        return user

    user_info = user_info[0]
    user['avatar'] = str(user_info.avatar)
    user['gender'] = str(user_info.gender)
    user['phone'] = user_info.phone
    user['auth'] = str(user_info.auth)
    user['auth_info'] = user_info.auth_info
    user['real_name'] = user_info.real_name
    user['other'] = user_info.other

    collection_dict = dict()
    for t in user_info.collections.all():
        collection_dict[str(t.id)] = t.name
    user['collections'] = json.dumps(collection_dict)
    subscribe_dict = dict()
    borrow_dict = dict()
    return_dict = dict()
    active_books = models.ActiveRecord.objects.filter(uid=user_info)
    if active_books:
        for active_book in active_books:
            book_instance = models.BookInstance.objects.get(id=active_book.bid_id)
            book = models.BookInfo.objects.get(id=book_instance.bid_id)
            if active_book.active == 0:
                subscribe_dict[str(book.id)] = book.name
            elif active_book.active == 1:
                borrow_dict[str(book.id)] = book.name
            elif active_book.active == 2:
                return_dict[str(book.id)] = book.name

    user['subscribed'] = json.dumps(subscribe_dict)
    user['borrowed'] = json.dumps(borrow_dict)
    user['returned'] = json.dumps(return_dict)
    return user


def comment_to_dict(obj):
    comment_content = dict()
    comment_content["id"] = str(obj.id)
    comment_content["comment_time"] = str(obj.comment_time)
    comment_content["content"] = obj.content
    comment_content["user_id"] = str(obj.uid_id)
    comment_content["parent_id"] = str(obj.parent_comment_id)

    agree_times = models.AttitudeRecord.objects.filter(cid=obj, attitude=0).count()
    disagree_times = models.AttitudeRecord.objects.filter(cid=obj, attitude=1).count()
    reported_times = models.AttitudeRecord.objects.filter(cid=obj, attitude=1).count()
    comment_content["agree_times"] = str(agree_times)
    comment_content["disagree_times"] = str(disagree_times)
    comment_content["reported_times"] = str(reported_times)

    return comment_content

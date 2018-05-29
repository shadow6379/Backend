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

    return user



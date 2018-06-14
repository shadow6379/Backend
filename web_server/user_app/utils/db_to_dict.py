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

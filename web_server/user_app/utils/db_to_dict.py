import json


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


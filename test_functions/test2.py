
def check_media(value):
    allowed_type = ['mp4','png', 'jpg', 'jpeg']
    if len(value) > 30:
        return 'слишком много медиафайлов'
    for i in value:
        if i not in allowed_type:
            return 'недопустимый тип файлов'
        if i == 'mp4' and len(value) > 1:
            return 'количество mp4 !> 1'
        if (i in ['png', 'jpg', 'jpeg']) and len(value) > 30:
            return 'слишком много image'
    return 'nice'

my_media_1 = ['png', 'jpg', 'jpeg',]
my_media_2 = ['mp4', 'png']
my_media_3 = ['mp42']

my_media_4 = ['png', 'jpg', 'jpeg','png', 'jpg', 'jpeg','png', 'jpg', 'jpeg','png', 'jpg', 'jpeg','png', 'jpg', 'jpeg','png', 'jpg', 'jpeg','png', 'jpg', 'jpeg','png', 'jpg', 'jpeg','png', 'jpg', 'jpeg','png', 'jpg', 'jpeg','png', 'jpg', 'jpeg','png', 'jpg', 'jpeg',]

print(check_media(my_media_1))
print(check_media(my_media_2))
print(check_media(my_media_3))
print(check_media(my_media_4))
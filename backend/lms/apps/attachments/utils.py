from django.db.models.functions.datetime import datetime


def get_default_filename(instance, filename):
    _datetime = datetime.now()
    datetime_str = _datetime.strftime("%Y-%m-%d-%H-%M-%S")
    file_name_split = filename.split('.')
    file_name_list = file_name_split[:-1]
    ext = file_name_split[-1]
    file_name_wo_ext = '.'.join(file_name_list)
    return "{0}__{1}.{2}".format(file_name_wo_ext, datetime_str, ext)


def get_default_upload_file_name(instance, filename):
    return 'attachments/{}'.format(get_default_filename(instance, filename))


def get_file_type_from_extension(extension: str):
    extension = extension.lower()
    if extension in ['jpg', 'jpeg', 'png', 'gif']:
        return 'image'
    elif extension in ['mp4', 'avi', 'mov']:
        return 'video'
    elif extension in ['mp3', 'wav']:
        return 'audio'
    elif extension in ['pdf', 'docx', 'txt']:
        return 'document'
    else:
        return 'file'

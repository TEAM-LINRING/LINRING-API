from django.conf import settings  # import the settings file


def get_url_front(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'URL_FRONT': settings.URL_FRONT}

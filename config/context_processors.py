from django.conf import settings


def site_info(request):
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'ToriChat'),
        'BOT_NAME': getattr(settings, 'BOT_NAME', 'Tori'),
    }


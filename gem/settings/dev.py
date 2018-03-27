from .base import *  # noqa


ALLOWED_HOSTS = [
    'localhost',
    '.localhost'
]

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *  # noqa
except ImportError:
    pass

try:
    from secrets import *  # noqa
except ImportError:
    pass


LOGGING = {
    'version': 1,
    'loggers': {
        'django': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        'django.template': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
}

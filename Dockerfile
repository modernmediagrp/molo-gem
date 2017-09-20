ARG MOLO_VERSION=5
FROM praekeltfoundation/molo-bootstrap:${MOLO_VERSION}-onbuild

ENV DJANGO_SETTINGS_MODULE=gem.settings.docker \
    CELERY_APP=gem

RUN LANGUAGE_CODE=en django-admin compilemessages && \
    django-admin collectstatic --noinput && \
    django-admin compress

CMD ["gem.wsgi:application", "--timeout", "1800"]

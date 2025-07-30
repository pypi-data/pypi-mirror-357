from cookie_notification.utils import (
    get_agreement_from_request,
)


def set_cookie_notification_notified_middleware(get_response):
    """
    Django-middleware, проставляющий cookie, отмечающий, что
    пользователь оповещен об их использовании.
    """

    def middleware(request):
        response = get_response(request)

        if get_agreement_from_request(request):
            response.set_cookie('userNotifiedAboutCookieUsage', 't', httponly=False)

        return response

    return middleware

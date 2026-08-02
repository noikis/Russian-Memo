from django.conf import settings


class SameSiteNoneCompatMiddleware:
    """
    Add SameSite=None on older Django versions that cannot emit it themselves.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self._patch_cookie(
            response,
            settings.SESSION_COOKIE_NAME,
            getattr(settings, 'SESSION_COOKIE_SAMESITE_NONE', False),
        )
        self._patch_cookie(
            response,
            settings.CSRF_COOKIE_NAME,
            getattr(settings, 'CSRF_COOKIE_SAMESITE_NONE', False),
        )
        return response

    @staticmethod
    def _patch_cookie(response, cookie_name, use_samesite_none):
        if not use_samesite_none or cookie_name not in response.cookies:
            return

        response.cookies[cookie_name]['samesite'] = 'None'
        response.cookies[cookie_name]['secure'] = True

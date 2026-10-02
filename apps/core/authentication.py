from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication that skips internal CSRF validation for authenticated API views,
    preventing reverse-proxy SSL and CSRF cookie mismatches in production while keeping
    IsAuthenticated permission checks strictly intact.
    """
    def enforce_csrf(self, request):
        return None

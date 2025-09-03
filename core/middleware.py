# core/middleware.py
from django.utils.deprecation import MiddlewareMixin
from core.thread_local import set_current_user, clear_current_user

class ThreadLocalUserMiddleware(MiddlewareMixin):
    """After auth, stash request.user in thread-local storage."""
    def process_request(self, request):
        # At this point request.user is already set by AuthenticationMiddleware
        set_current_user(getattr(request, "user", None))

    def process_response(self, request, response):
        clear_current_user()
        return response

    def process_exception(self, request, exception):
        clear_current_user()
        # Let Django still handle the exception
        return None

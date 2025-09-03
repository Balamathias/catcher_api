import logging
from django.template.response import TemplateResponse
from django.http import JsonResponse
from supabase import create_client, Client

from utils.response import ResponseMixin
from services.supabase import supabase
from django.conf import settings

logger = logging.getLogger(__name__)


class SupabaseJWTMiddleware(ResponseMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            user_info = self.verify_supabase_token(token)

            if user_info:
                request.supabase_user = user_info
                # Create new authenticated supabase client instance
                request.supabase_client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )

                request.token = token
                
                request.supabase_client.headers = {
                    "Authorization": f"Bearer {token}"
                }
            else:
                return JsonResponse({"detail": "Invalid Supabase or expired token"}, status=401)
        else:
            request.supabase_user = None
            request.supabase_client = supabase

        response = self.get_response(request)
        if isinstance(response, TemplateResponse):
            response.render()
        return response

    def verify_supabase_token(self, token):
        try:
            resp = supabase.auth.get_user(jwt=token)

            if getattr(resp, "error", None):
                logger.warning("Supabase auth error: %s", resp)
                return None

            user_data = getattr(resp, "data", None) or getattr(resp, "user", None)
            return user_data

        except Exception:
            logger.exception("Error verifying Supabase token")
            return None

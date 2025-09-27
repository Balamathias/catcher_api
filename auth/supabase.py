from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import logging

from services.supabase import supabase, superbase

logger = logging.getLogger(__name__)

class SupabaseUser:
    """A simple user object that mimics Django's User."""
    def __init__(self, user_data: dict):
        self.id       = user_data.get("id")
        self.email    = user_data.get("email")
        self.phone    = user_data.get("phone")
        self.metadata = user_data.get("user_metadata") or user_data.get("metadata")
        try:
            self.role = superbase.table('profile').select('role').eq('id', self.id).single().execute().data.get('role', 'user')
        except:
            pass

    @property
    def is_authenticated(self):
        return True
    

class SupabaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ", 1)[1]
        user_data = self.verify_token_with_supabase(token)

        if not user_data:
            raise AuthenticationFailed("Invalid or expired Supabase token")

        user = SupabaseUser(user_data)

        return SupabaseUser(user_data), None

    def authenticate_header(self, request):
        return "Bearer"

    def verify_token_with_supabase(self, token):
        """
        Uses supabase-py to validate a JWT. Requires SUPABASE_KEY=service_role.
        """
        try:
            auth_resp = supabase.auth.get_user(jwt=token)

            user_model = getattr(auth_resp, "user", None) or \
                         getattr(auth_resp, "data", None)

            if not user_model:
                logger.warning("No user data in Supabase auth response: %r", auth_resp)
                return None

            if hasattr(user_model, "dict"):
                return user_model.dict()

            return user_model

        except Exception:
            logger.exception("Error verifying Supabase token")
            return None


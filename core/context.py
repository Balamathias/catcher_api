"""
Context management for agent functions.

This module provides utilities for managing request context and user information
across function calls, making it available to agent tools without explicitly passing
it through each function call.
"""

import logging
import threading
from functools import wraps
from typing import Optional, Any, Dict, Callable

from django.contrib.auth import get_user_model

# Set up context logger
logger = logging.getLogger('core.context')
logger.setLevel(logging.DEBUG)

# Create a handler if none exists
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Thread-local storage
_local = threading.local()

User = get_user_model()

class AgentContext:
    """Manages context data for agent functions."""
    
    @staticmethod
    def set_context(key: str, value: Any):
        """Set a value in the current context."""
        if not hasattr(_local, 'context'):
            _local.context = {}
        _local.context[key] = value
        logger.debug(f"Context set: {key}={str(value)[:50]}")
    
    @staticmethod
    def get_context(key: str, default: Any = None) -> Any:
        """Get a value from the current context."""
        if not hasattr(_local, 'context') or key not in _local.context:
            logger.debug(f"Context key '{key}' not found, returning default: {default}")
            return default
        value = _local.context[key]
        logger.debug(f"Context retrieved: {key}={str(value)[:50]}")
        return value
    
    @staticmethod
    def clear_context():
        """Clear all context data."""
        if hasattr(_local, 'context'):
            logger.debug(f"Clearing context with {len(_local.context)} items")
            del _local.context
    
    @staticmethod
    def set_current_user(user):
        """Set the current user in context."""
        AgentContext.set_context('user', user)
        if user:
            logger.info(f"Set current user in context: user_id={str(user.id)}")
    
    @staticmethod
    def get_current_user():
        """Get the current user from context."""
        return AgentContext.get_context('user')
    
    @staticmethod
    def get_current_user_id() -> Optional[str]:
        """Get the current user ID as string."""
        user = AgentContext.get_current_user()
        return str(user.id) if user and hasattr(user, 'id') else None
    
    @staticmethod
    def get_current_institution():
        """Get the current user's institution."""
        user = AgentContext.get_current_user()
        return user.institution if user and hasattr(user, 'institution') else None
    
    @staticmethod
    def get_current_institution_id() -> Optional[str]:
        """Get the current user's institution ID as string."""
        institution = AgentContext.get_current_institution()
        return str(institution.id) if institution and hasattr(institution, 'id') else None


class UserContextManager:
    """Context manager for setting user context temporarily."""
    
    def __init__(self, user):
        self.user = user
        self.previous_user = None
    
    def __enter__(self):
        self.previous_user = AgentContext.get_current_user()
        AgentContext.set_current_user(self.user)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.previous_user:
            AgentContext.set_current_user(self.previous_user)
        else:
            # No previous user, clear current user
            AgentContext.set_context('user', None)


def with_user_context(func):
    """
    Decorator that injects user context into function calls.
    If user_id is provided as an argument, it will be used to fetch the user.
    Otherwise, the current user from context will be used.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if user_id is in kwargs
        if 'user_id' in kwargs:
            user_id = kwargs.get('user_id')
            if user_id:
                try:
                    # Try to fetch the user
                    user = User.objects.get(id=user_id)
                    # Set as current user temporarily
                    with UserContextManager(user):
                        return func(*args, **kwargs)
                except User.DoesNotExist:
                    # If user doesn't exist, continue with current context
                    pass
        
        # If user_id not provided or user doesn't exist, use current context
        return func(*args, **kwargs)
    
    return wrapper

# Helper function to add context to function parameters automatically
def inject_context(kwargs):
    """
    Inject context variables (user, institution) into kwargs if not already present.
    """
    original_kwargs = kwargs.copy()
    
    if 'user_id' not in kwargs:
        user_id = AgentContext.get_current_user_id()
        if user_id:
            kwargs['user_id'] = user_id
            logger.debug(f"Injected user_id={user_id} into function arguments")
            
    if 'institution_id' not in kwargs:
        institution_id = AgentContext.get_current_institution_id()
        if institution_id:
            kwargs['institution_id'] = institution_id
            logger.debug(f"Injected institution_id={institution_id} into function arguments")

    # Log what was injected
    added_context = {k: v for k, v in kwargs.items() if k not in original_kwargs}
    if added_context:
        logger.info(f"Context injected: {added_context}")
            
    return kwargs


# Export from module for backwards compatibility
current_user = AgentContext.get_current_user
current_user_id = AgentContext.get_current_user_id
set_current_user = AgentContext.set_current_user

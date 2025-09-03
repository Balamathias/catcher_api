import os

from rest_framework.response import Response
from rest_framework import status as drf_status

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.template import TemplateDoesNotExist
from django.conf import settings


from django.core.mail import send_mail

import logging

logger = logging.getLogger(__name__)


def ensure_template_directories():
    """
    Ensure that template directories exist for emails.
    Creates them if they don't exist.
    """
    template_dirs = [
        os.path.join(settings.BASE_DIR, 'templates'),
        os.path.join(settings.BASE_DIR, 'templates', 'emails')
    ]
    
    for directory in template_dirs:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                logger.info(f"Created template directory: {directory}")
            except Exception as e:
                logger.error(f"Failed to create template directory {directory}: {str(e)}")

def render_email_template(template_name, context=None):
    """
    Renders an HTML email template with the given context.
    Returns both HTML and plain text versions.
    
    Args:
        template_name: Name of the template (without extension)
        context: Dictionary of context variables for the template
    
    Returns:
        tuple: (html_content, plain_text_content)
    """
    if context is None:
        context = {}
        
    if 'APP_NAME' not in context:
        from utils.constants import APP_NAME
        context['APP_NAME'] = APP_NAME
        
    if 'BASE_URL' not in context:
        context['BASE_URL'] = os.environ.get('FRONTEND_URL', 'https://lawstack.ai')
    
    from datetime import datetime
    context['current_year'] = datetime.now().year
    
    ensure_template_directories()
    
    try:
        html_content = render_to_string(f'emails/{template_name}.html', context)
        
        plain_text_content = strip_tags(html_content)
        
        return html_content, plain_text_content
    
    except TemplateDoesNotExist:
        logger.error(f"Email template not found: emails/{template_name}.html")
        return generate_fallback_email(template_name, context)
    except Exception as e:
        logger.error(f"Error rendering email template {template_name}: {str(e)}")
        return generate_fallback_email(template_name, context)

def generate_fallback_email(template_type, context):
    """
    Generate a basic fallback email when the template is not found.
    
    Args:
        template_type: The type of email being sent (otp_verification, welcome, etc.)
        context: The context data for the email
    
    Returns:
        tuple: (html_content, plain_text_content)
    """
    app_name = context.get('APP_NAME', 'LawStack')
    
    if template_type == 'otp_verification':
        otp = context.get('otp', 'N/A')
        username = context.get('username', context.get('user_email', 'User'))
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{app_name} - Verification Code</title>
        </head>
        <body>
            <h2>Your Verification Code</h2>
            <p>Hello {username},</p>
            <p>Your verification code is: <strong>{otp}</strong></p>
            <p>This code will expire in 15 minutes.</p>
            <p>Thank you,<br>{app_name} Team</p>
        </body>
        </html>
        """
    
    elif template_type == 'welcome':
        username = context.get('username', context.get('user_email', 'User'))
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Welcome to {app_name}</title>
        </head>
        <body>
            <h2>Welcome to {app_name}!</h2>
            <p>Hello {username},</p>
            <p>Thank you for joining {app_name}. We're excited to have you on board!</p>
            <p>Thank you,<br>{app_name} Team</p>
        </body>
        </html>
        """
    
    elif template_type == 'password_reset':
        username = context.get('username', context.get('user_email', 'User'))
        reset_url = context.get('reset_url', '#')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{app_name} - Password Reset</title>
        </head>
        <body>
            <h2>Password Reset</h2>
            <p>Hello {username},</p>
            <p>You've requested a password reset. Click the link below to set a new password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>Thank you,<br>{app_name} Team</p>
        </body>
        </html>
        """
    
    else:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{app_name} Notification</title>
        </head>
        <body>
            <h2>{app_name} Notification</h2>
            <p>This is an automated message from {app_name}.</p>
            <p>Thank you,<br>{app_name} Team</p>
        </body>
        </html>
        """
    
    plain_text_content = strip_tags(html_content)
    return html_content, plain_text_content

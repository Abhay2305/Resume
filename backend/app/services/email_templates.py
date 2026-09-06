"""Email templates service.

Provides reusable HTML email templates for authentication flows.
Templates are rendered with Jinja2 for dynamic content.
"""
import os
from typing import Dict, Any


# Base URL for links (configurable via environment)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def _base_template(title: str, content: str) -> str:
    """Wrap content in a consistent email template."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f4f4f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
            <tr>
                <td align="center" style="padding: 40px 20px;">
                    <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #7BC4BE 0%, #4A9E98 100%); padding: 32px; text-align: center;">
                                <h1 style="margin: 0; color: #1A2B2A; font-size: 24px; font-weight: 700;">
                                    &#10022; PromptResume
                                </h1>
                            </td>
                        </tr>
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 32px;">
                                {content}
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f9fafb; padding: 24px 32px; text-align: center; border-top: 1px solid #e5e7eb;">
                                <p style="margin: 0; color: #6b7280; font-size: 12px;">
                                    If you didn't request this email, you can safely ignore it.
                                </p>
                                <p style="margin: 8px 0 0; color: #9ca3af; font-size: 11px;">
                                    &copy; 2026 PromptResume. All rights reserved.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def verification_email(name: str, verification_url: str) -> Dict[str, str]:
    """Generate email verification template.
    
    Args:
        name: User's full name
        verification_url: Full URL with verification token
        
    Returns:
        Dict with 'subject' and 'html' keys
    """
    content = f"""
        <h2 style="margin: 0 0 16px; color: #1f2937; font-size: 20px;">Verify your email address</h2>
        <p style="margin: 0 0 16px; color: #4b5563; font-size: 16px; line-height: 1.5;">
            Hi {name or 'there'},
        </p>
        <p style="margin: 0 0 24px; color: #4b5563; font-size: 16px; line-height: 1.5;">
            Welcome to PromptResume! Please verify your email address to activate your account and start building professional resumes.
        </p>
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto 24px;">
            <tr>
                <td style="background: linear-gradient(135deg, #7BC4BE 0%, #4A9E98 100%); border-radius: 8px;">
                    <a href="{verification_url}" style="display: inline-block; padding: 14px 32px; color: #1A2B2A; font-size: 16px; font-weight: 600; text-decoration: none;">
                        Verify Email Address
                    </a>
                </td>
            </tr>
        </table>
        <p style="margin: 0 0 16px; color: #6b7280; font-size: 14px; line-height: 1.5;">
            This verification link will expire in 24 hours.
        </p>
        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.5;">
            If the button doesn't work, copy and paste this link into your browser:<br>
            <a href="{verification_url}" style="color: #4A9E98; word-break: break-all;">{verification_url}</a>
        </p>
    """
    return {
        "subject": "Verify your PromptResume email address",
        "html": _base_template("Verify Email", content),
    }


def password_reset_email(name: str, reset_url: str) -> Dict[str, str]:
    """Generate password reset template.
    
    Args:
        name: User's full name
        reset_url: Full URL with reset token
        
    Returns:
        Dict with 'subject' and 'html' keys
    """
    content = f"""
        <h2 style="margin: 0 0 16px; color: #1f2937; font-size: 20px;">Reset your password</h2>
        <p style="margin: 0 0 16px; color: #4b5563; font-size: 16px; line-height: 1.5;">
            Hi {name or 'there'},
        </p>
        <p style="margin: 0 0 24px; color: #4b5563; font-size: 16px; line-height: 1.5;">
            We received a request to reset your password. Click the button below to create a new password.
        </p>
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto 24px;">
            <tr>
                <td style="background: linear-gradient(135deg, #7BC4BE 0%, #4A9E98 100%); border-radius: 8px;">
                    <a href="{reset_url}" style="display: inline-block; padding: 14px 32px; color: #1A2B2A; font-size: 16px; font-weight: 600; text-decoration: none;">
                        Reset Password
                    </a>
                </td>
            </tr>
        </table>
        <p style="margin: 0 0 16px; color: #6b7280; font-size: 14px; line-height: 1.5;">
            This reset link will expire in 30 minutes.
        </p>
        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.5;">
            If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.
        </p>
    """
    return {
        "subject": "Reset your PromptResume password",
        "html": _base_template("Reset Password", content),
    }


def welcome_email(name: str) -> Dict[str, str]:
    """Generate welcome email template.
    
    Args:
        name: User's full name
        
    Returns:
        Dict with 'subject' and 'html' keys
    """
    content = f"""
        <h2 style="margin: 0 0 16px; color: #1f2937; font-size: 20px;">Welcome to PromptResume!</h2>
        <p style="margin: 0 0 16px; color: #4b5563; font-size: 16px; line-height: 1.5;">
            Hi {name or 'there'},
        </p>
        <p style="margin: 0 0 24px; color: #4b5563; font-size: 16px; line-height: 1.5;">
            Thank you for joining PromptResume! You're now ready to create professional, ATS-optimized resumes with the power of AI.
        </p>
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto 24px;">
            <tr>
                <td style="background: linear-gradient(135deg, #7BC4BE 0%, #4A9E98 100%); border-radius: 8px;">
                    <a href="{FRONTEND_URL}/dashboard" style="display: inline-block; padding: 14px 32px; color: #1A2B2A; font-size: 16px; font-weight: 600; text-decoration: none;">
                        Go to Dashboard
                    </a>
                </td>
            </tr>
        </table>
        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.5;">
            Here's what you can do with PromptResume:
        </p>
        <ul style="margin: 16px 0; padding-left: 20px; color: #4b5563; font-size: 14px; line-height: 1.8;">
            <li>Create AI-powered resumes tailored to job descriptions</li>
            <li>Get your resume scored for ATS compatibility</li>
            <li>Generate professional cover letters</li>
            <li>Access intelligent career insights</li>
        </ul>
    """
    return {
        "subject": "Welcome to PromptResume!",
        "html": _base_template("Welcome", content),
    }


def account_deletion_email(name: str) -> Dict[str, str]:
    """Generate account deletion confirmation template.
    
    Args:
        name: User's full name
        
    Returns:
        Dict with 'subject' and 'html' keys
    """
    content = f"""
        <h2 style="margin: 0 0 16px; color: #1f2937; font-size: 20px;">Account Deletion Confirmed</h2>
        <p style="margin: 0 0 16px; color: #4b5563; font-size: 16px; line-height: 1.5;">
            Hi {name or 'there'},
        </p>
        <p style="margin: 0 0 24px; color: #4b5563; font-size: 16px; line-height: 1.5;">
            Your PromptResume account has been successfully deactivated. Your data has been preserved for audit purposes but is no longer accessible.
        </p>
        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.5;">
            If you change your mind, you can contact our support team within 30 days to reactivate your account.
        </p>
    """
    return {
        "subject": "Your PromptResume account has been deactivated",
        "html": _base_template("Account Deleted", content),
    }

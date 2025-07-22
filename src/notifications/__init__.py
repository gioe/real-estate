"""
Notifications Module

This package handles sending notifications for property alerts
via email, SMS, and webhook channels.
"""

from .notification_system import NotificationManager

__all__ = [
    'NotificationManager'
]

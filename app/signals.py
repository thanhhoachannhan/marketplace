
import logging

from django.contrib.auth.signals import (
    user_logged_in,
    user_login_failed,
    user_logged_out,
)
from django.dispatch import receiver


logger = logging.getLogger('django')

@receiver(user_logged_in)
def post_login(sender, request, user, **kwargs):
    logger.info(f'User: {user.username} logged in')

@receiver(user_logged_out)
def post_logout(sender, request, user, **kwargs):
    logger.info(f'User: {user.username} logged out')

@receiver(user_login_failed)
def post_login_fail(sender, credentials, request, **kwargs):
    logger.info(f'Login failed with credentials: {credentials}')

"""
ASGI config for SocialNetwork project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

# from channels.routing import ProtocolTypeRouter
# from channels.security.websocket import
# django_asgi_app = get_asgi_application()
#
#
# application = ProtocolTypeRouter({
#     'http': django_asgi_app,
#     # "websocket":
# })

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SocialNetwork.settings')

application = get_asgi_application()
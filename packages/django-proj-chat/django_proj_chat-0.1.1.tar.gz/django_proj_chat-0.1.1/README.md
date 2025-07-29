# Django Proj Chat
A reusable Django app for real-time instant messaging using Django Channels and Redis.  

## Installation

1. Install the package and dependencies:
```bash
pip install django-proj-chat django==5.0.* channels==4.0.* channels-redis==4.0.* daphne==4.0.*
```


2. Add to INSTALLED_APPS in your project's settings.py:
```python
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'channels',
    'chat',
]
```


3. Configure Channels in settings.py:
```python
ASGI_APPLICATION = 'your_project.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

4. Update asgi.py in your project:
```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
```

5. Include URLs in your project's urls.py:
```python
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),  # Uses chat/urls.py from django-proj-chat
    path('login/', auth_views.LoginView.as_view(template_name='chat/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
```

6. Install and run Redis:

Install Redis (e.g., sudo apt install redis-server on Ubuntu).
Start Redis:  
```redis-server```


7. Run migrations to create the chat database tables:
```bash
python manage.py migrate
```

8. Add STATIC_ROOT and STATICFILES_DIRS to settings.py. Collect static files for the chat app’s CSS:
```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'chat' / 'static']
```

```bash 
python manage.py collectstatic
```


## Customization

Templates: Override templates by creating your_project/templates/chat/ and copying files from chat/templates/chat/. Modify chat.html or messages.html for your project’s style.
Styling: Extend chat/static/chat/styles.css by adding custom CSS in your_project/static/.
Logic: Subclass chat/views.py or chat/consumers.py for custom behavior (e.g., linking to user profiles in a dating site).

## Requirements

Django 5.0+
Channels 4.0+
Channels-Redis 4.0+
Daphne 4.0+  # Required for WebSocket handling
Redis server

## Notes

The chat app, including chat/urls.py, is provided by the django-proj-chat package. Do not create a new chat app with python manage.py startapp chat, as it will conflict with the packaged app.
Ensure Redis and Daphne are installed and running before starting the Django server for real-time messaging.


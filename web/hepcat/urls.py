"""hepcat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import home_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home_view, name='home'),
    path('', include('classwork.urls')),
    path('user/', include('django.contrib.auth.urls')),
    path('user/', include('users.urls')),
    path('admin/', admin.site.urls),
    path('payments/', include('payments.urls')),
    # path('newsletter/', include('newsletter.urls')),  # subscribe, unsubscribe, archive features
]

if settings.DEBUG is True:  # pragma: no cover
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Thanks to django-newsletter, the following paths are set:
# newsletter/ ???
# Thanks to django-payments, the following paths are set:
# payments/process/<token-regex>/ [name=process_data]
# payments/process/<variant-regex>/ [static_process_payment]
# Thanks to django.contrib.auth.urls The following paths are set:
# user/login/ [name='login']
# user/logout/ [name='logout']
# user/password_change/ [name='password_change']
# user/password_change/done/ [name='password_change_done']
# user/password_reset/ [name='password_reset']
# user/password_reset/done/ [name='password_reset_done']
# user/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# user/reset/done/ [name='password_reset_complete']

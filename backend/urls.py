"""
URL configuration for backend project.
"""

from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Accounts and Quiz API
    path(
        'api/accounts/',
        include('accounts.urls')
    ),
]
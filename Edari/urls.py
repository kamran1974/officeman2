from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls')),
    path('', include('shop.urls')),
    path('', include('organization.urls')),
]
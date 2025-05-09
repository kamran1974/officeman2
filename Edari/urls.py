from django.contrib import admin
from django.urls import path, include
<<<<<<< HEAD
=======
from django.conf import settings
from django.conf.urls.static import static

>>>>>>> 3d29c33 (New feature TODOLIST added)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls')),
    path('', include('shop.urls')),
    path('', include('organization.urls')),
]
<<<<<<< HEAD
=======

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
>>>>>>> 3d29c33 (New feature TODOLIST added)

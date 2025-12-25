from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api_v1.views.recipes import redirect_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api_v1.urls')),
    # Путь для короткой ссылке на получение рецепта.
    path('s/<str:short_id>/',
         redirect_view,
         name='short-link'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

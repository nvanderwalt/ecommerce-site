from django.contrib import admin
from django.urls import path
from inventory.views import product_list, add_to_cart

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', product_list, name='product_list'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

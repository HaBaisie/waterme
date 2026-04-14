from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def api_home(request):
    return JsonResponse(
        {
            'name': 'Water Mi MVP API',
            'status': 'ok',
            'docs': '/api/docs/',
            'schema': '/api/schema/',
            'routes': {
                'auth': '/api/auth/',
                'users': '/api/users/',
                'vendors': '/api/vendors/',
                'orders': '/api/orders/',
            },
        }
    )

urlpatterns = [
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui-root'),
    path('api/', api_home, name='api-home'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/users/', include('accounts.urls_user')),
    path('api/vendors/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
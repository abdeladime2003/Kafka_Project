from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from review.views import ReviewViewSet

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

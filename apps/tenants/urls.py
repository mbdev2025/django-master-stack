from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, TeamViewSet, MemberViewSet

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'members', MemberViewSet, basename='member')

urlpatterns = [
    path('', include(router.urls)),
]

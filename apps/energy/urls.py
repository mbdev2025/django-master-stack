from django.urls import path
from .views import StartEnedisAuthView, EnedisCallbackView, CreateAccessRequestView, SyncSandboxDataView

urlpatterns = [
    path('auth/init/', StartEnedisAuthView.as_view(), name='enedis-auth-init'),
    path('auth/callback/', EnedisCallbackView.as_view(), name='enedis-auth-callback'),
    path('installer/invite/', CreateAccessRequestView.as_view(), name='installer-invite'),
    path('sandbox/sync/', SyncSandboxDataView.as_view(), name='sandbox-sync'),
]

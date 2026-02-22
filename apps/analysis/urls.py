from django.urls import path
from . import views

urlpatterns = [
    path('', views.solar_analysis, name='analysis_solar'),
    path('upload/', views.upload_document, name='upload_document'),
    path('documents/list/', views.list_documents, name='list_documents'),
]

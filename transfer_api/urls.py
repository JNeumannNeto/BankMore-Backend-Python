from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_transfer, name='transfer-create'),
    path('list/', views.list_transfers, name='transfer-list'),
    path('<uuid:transfer_id>/', views.get_transfer, name='transfer-detail'),
]

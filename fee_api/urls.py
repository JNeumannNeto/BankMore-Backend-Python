from django.urls import path
from . import views

urlpatterns = [
    path('<str:account_number>/', views.get_fees_by_account_number, name='fee-list-by-account'),
    path('detail/<uuid:fee_id>/', views.get_fee_by_id, name='fee-detail'),
    path('my/', views.get_my_fees, name='fee-my-list'),
]

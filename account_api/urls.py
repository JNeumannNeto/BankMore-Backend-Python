from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='account-register'),
    path('login/', views.login, name='account-login'),
    path('deactivate/', views.deactivate, name='account-deactivate'),
    path('movement/', views.movement, name='account-movement'),
    path('balance/', views.balance, name='account-balance'),
    path('exists/<str:account_number>/', views.account_exists, name='account-exists'),
    path('balance/<str:account_number>/', views.balance_by_account_number, name='account-balance-by-number'),
]

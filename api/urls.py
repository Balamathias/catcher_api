from django.urls import path
from api.views import (ItemsAPIView, health_check, 
                        SearchRegistry, ItemsAnalyticsAPIView, PaystackPaymentAPIView, paystack_callback, UserCreditsAPIView
                       )


urlpatterns = [
    path('health/', health_check, name='health-check'),

    path('items/', ItemsAPIView.as_view(), name='items-list'),
    path('items/<uuid:item_id>/', ItemsAPIView.as_view(), name='items-detail'),
    path('items/analytics/', ItemsAnalyticsAPIView.as_view(), name='items-analytics'),
    path('payments/initiate/', PaystackPaymentAPIView.as_view(), name='payments-initiate'),
    path('payments/verify/', PaystackPaymentAPIView.as_view(), name='payments-verify'),
    path('payments/credits/', UserCreditsAPIView.as_view(), name='payments-credits'),
    path('payments/callback/', paystack_callback, name='payments-callback'),

    path('registry/search/', SearchRegistry.as_view(), name='search-registry'),
    
]
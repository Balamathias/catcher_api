from django.urls import path
from api.views import ItemsAPIView


urlpatterns = [
    path('items/', ItemsAPIView.as_view(), name='items-list'),
    path('items/<int:item_id>/', ItemsAPIView.as_view(), name='items-detail'),
]
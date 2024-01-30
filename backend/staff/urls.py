from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='products'),
    path('change_product/<slug:slug>', views.change_product, name='change_product'),
    path('delete_product/<slug:slug>', views.delete_product, name='delete_product'),
    path('cats/', views.CategoryListView.as_view(), name='cat_list'),

    path('orders_active/', views.ActiveOrderListView.as_view(), name='active_orders'),
    path('orders_completed/', views.CompletedOrderListView.as_view(), name='completed_orders'),
    path('order_detail/<int:order_id>', views.order_detail, name='order_detail'),
    path('order_cancel/<int:order_id>', views.order_cancel, name='order_cancel'),
]
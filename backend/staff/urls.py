from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='products'),
    path('product/<slug:slug>/', views.product_detail_view, name='product-detail'),
    path('add_product/', views.ProductAddView.as_view(), name='add_product'),
    path('change_product/<slug:slug>', views.change_product, name='change_product'),
    path('delete_product/<slug:slug>', views.delete_product, name='delete_product'),
    path('search_product/', views.search_products, name='search_products'),

    path('orders_active/', views.ActiveOrderListView.as_view(), name='active_orders'),
    path('orders_completed/', views.CompletedOrderListView.as_view(), name='completed_orders'),
    path('order_detail/<int:order_id>', views.order_detail, name='order_detail'),
    path('order_cancel/<int:order_id>', views.order_cancel, name='order_cancel'),

    path('mailing/', views.email_sending, name='mailing'),
    path('promo/', views.list_promo, name='promo'),
    path('add_promo/', views.add_promo, name='add_promo'),
]
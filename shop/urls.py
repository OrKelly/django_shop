from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.products_view, name='products'),
    path('<slug:slug>/', views.product_detail_view, name='product-detail'),
    path('category/<slug:slug>', views.categories_list, name='category-list'),
]
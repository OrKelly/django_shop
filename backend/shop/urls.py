from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    #path('', views.products_view, name='products'),
    path('', views.ProductListView.as_view(), name='products'),
    path('sales/', views.SalesListView.as_view(), name='sales'),
    path("search_products/", views.search_products, name="search-products"),
    path('<slug:slug>/', views.product_detail_view, name='product-detail'),
    path('category/<slug:slug>', views.categories_list, name='category-list'),
]
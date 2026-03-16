# my_all_in/urls.py

from django.urls import path
from . import views

app_name = 'my_all_in'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    path('auth/', views.auth, name='auth'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('categories/<int:category_id>/', views.category_products, name='category_products'),

    # Товары
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_item/', views.add_item, name='add_item'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('product/<int:product_id>/delete/', views.product_delete, name='product_delete'),
]
# my_all_in/urls.py

from django.urls import path
from . import views

app_name = 'my_all_in'  # Используем то же имя, что и в шаблоне

urlpatterns = [
    path('', views.index, name='index'),
    path('auth/', views.auth, name='auth'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('categories/<int:category_id>/', views.category_products, name='category_products'),
]
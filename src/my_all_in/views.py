# my_all_in/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile, Product, Category, Order
from .forms import UserRegisterForm, UserLoginForm


def index(request):
    """Главная страница"""
    products = Product.objects.filter(is_active=True)[:8]  # Последние 8 товаров
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, "my_all_in/index.html", context)


def auth(request):
    """Страница авторизации"""
    # Если пользователь уже авторизован, перенаправляем на главную
    if request.user.is_authenticated:
        return redirect('my_all_in:index')

    form = UserLoginForm()
    context = {
        'form': form,
    }
    return render(request, "my_all_in/auth.html", context)


def login_view(request):
    """Обработка входа"""
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('my_all_in:index')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return redirect('my_all_in:auth')


def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('my_all_in:index')


def register(request):
    """Регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect('my_all_in:index')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Профиль создается автоматически через сигнал
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}! Теперь вы можете войти.')
            return redirect('my_all_in:auth')
    else:
        form = UserRegisterForm()

    return render(request, 'my_all_in/register.html', {'form': form})


@login_required
def profile(request):
    """Профиль пользователя"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_all_in/profile.html', {'orders': orders})


def product_list(request):
    """Список товаров"""
    products = Product.objects.filter(is_active=True)
    return render(request, 'my_all_in/product_list.html', {'products': products})


def product_detail(request, product_id):
    """Детальная страница товара"""
    product = Product.objects.get(id=product_id, is_active=True)
    return render(request, 'my_all_in/product_detail.html', {'product': product})


def category_products(request, category_id):
    """Товары по категории"""
    category = Category.objects.get(id=category_id)
    products = category.products.filter(is_active=True)
    return render(request, 'my_all_in/category_products.html', {
        'category': category,
        'products': products
    })
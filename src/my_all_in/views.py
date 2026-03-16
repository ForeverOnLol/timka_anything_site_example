# my_all_in/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Profile, Product, Category, Order
from .forms import UserRegisterForm, UserLoginForm, ProductForm


def index(request):
    """Главная страница"""
    products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, "my_all_in/index.html", context)


def auth(request):
    """Страница авторизации"""
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


def add_item(request):
    """Страница добавления товара"""
    form = ProductForm()
    users = User.objects.all().order_by('username')
    context = {
        'form': form,
        'users': users,
        'title': 'Добавление товара'
    }
    return render(request, "my_all_in/add_item.html", context)


@login_required
def product_create(request):
    """Создание нового товара"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            if not product.user_id:
                product.user = request.user
            product.save()
            form.save_m2m()
            messages.success(request, f'Товар "{product.name}" успешно добавлен!')
            return redirect('my_all_in:product_detail', product_id=product.id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = ProductForm()

    users = User.objects.all().order_by('username')
    context = {
        'form': form,
        'users': users,
        'title': 'Добавление товара'
    }
    return render(request, 'my_all_in/add_item.html', context)


def product_list(request):
    """Список всех товаров"""
    products = Product.objects.filter(is_active=True).select_related('user').prefetch_related('categories')

    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(categories__id=category_id)

    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(payload__icontains=search_query))

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'title': 'Каталог товаров'
    }
    return render(request, 'my_all_in/product_list.html', context)


def product_detail(request, product_id):
    """Детальная страница товара"""
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
        'title': product.name
    }
    return render(request, 'my_all_in/product_detail.html', context)


def category_products(request, category_id):
    """Товары по категории"""
    category = get_object_or_404(Category, id=category_id)
    products = category.products.filter(is_active=True)
    return render(request, 'my_all_in/category_products.html', {
        'category': category,
        'products': products
    })


@login_required
def product_edit(request, product_id):
    """Редактирование товара"""
    product = get_object_or_404(Product, id=product_id)

    if product.user != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет прав для редактирования этого товара')
        return redirect('my_all_in:product_detail', product_id=product.id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Товар "{product.name}" успешно обновлен!')
            return redirect('my_all_in:product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'title': f'Редактирование: {product.name}'
    }
    return render(request, 'my_all_in/add_item.html', context)


@login_required
def product_delete(request, product_id):
    """Удаление товара"""
    product = get_object_or_404(Product, id=product_id)

    if product.user != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет прав для удаления этого товара')
        return redirect('my_all_in:product_detail', product_id=product.id)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Товар "{product_name}" удален')
        return redirect('my_all_in:product_list')

    context = {
        'product': product,
        'title': f'Удаление товара: {product.name}'
    }
    return render(request, 'my_all_in/product_confirm_delete.html', context)
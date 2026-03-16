# my_all_in/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile


class UserLoginForm(AuthenticationForm):
    """Форма входа"""
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class UserRegisterForm(UserCreationForm):
    """Форма регистрации"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Поля профиля
    fio = forms.CharField(
        max_length=255,
        required=False,
        label='ФИО',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label='Телефон',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        required=False,
        label='Адрес',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'

        for field_name in ['password1', 'password2']:
            self.fields[field_name].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Обновляем или создаем профиль с дополнительными полями
            profile, created = Profile.objects.get_or_create(user=user)
            profile.fio = self.cleaned_data.get('fio')
            profile.phone = self.cleaned_data.get('phone')
            profile.address = self.cleaned_data.get('address')
            profile.save()
        return user


# forms.py
from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """
    Форма для добавления и редактирования товаров
    """
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-group'}),
        required=False,
        label='Категории'
    )

    class Meta:
        model = Product
        fields = ['name', 'payload', 'price', 'number', 'categories', 'user', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название товара',
                'maxlength': 300
            }),
            'payload': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Подробное описание товара, состав, характеристики...',
                'rows': 5
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'user': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'status-checkbox'
            })
        }
        labels = {
            'name': 'Название товара',
            'payload': 'Описание/состав',
            'price': 'Цена (₽)',
            'number': 'Количество на складе',
            'user': 'Владелец товара',
            'is_active': 'Товар активен'
        }
        help_texts = {
            'payload': 'Подробное описание товара, состав, характеристики',
            'number': 'Текущее количество товара в наличии'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поле user необязательным
        self.fields['user'].required = False
        # Добавляем пустой вариант для выбора пользователя
        self.fields['user'].empty_label = "-- Выберите владельца --"

        # Сортируем категории по имени
        self.fields['categories'].queryset = Category.objects.all().order_by('name')
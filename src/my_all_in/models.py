from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Дополнительная информация о пользователе
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        MANAGER = 'manager', 'Менеджер'
        CUSTOMER = 'customer', 'Клиент'
        GUEST = 'guest', 'Гость'

    # Связь один-к-одному со встроенным User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )

    fio = models.CharField(
        max_length=255,
        verbose_name='ФИО',
        blank=True,
        null=True
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        verbose_name='Роль'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата создания'
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Адрес'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон'
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        ordering = ['-created_at']

    def __str__(self):
        return self.fio or self.user.username

    def save(self, *args, **kwargs):
        if not self.fio and self.user:
            self.fio = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Category(models.Model):
    """
    Модель категории товаров
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название категории',
        db_index=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='categories',
        verbose_name='Создатель категории'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Модель товара
    """
    name = models.CharField(
        max_length=300,
        verbose_name='Название товара',
        db_index=True
    )
    payload = models.TextField(
        verbose_name='Описание/состав',
        help_text='Подробное описание товара, состав, характеристики'
    )
    number = models.PositiveIntegerField(
        verbose_name='Количество на складе',
        help_text='Текущее количество товара в наличии',
        default=0
    )

    categories = models.ManyToManyField(
        Category,
        related_name='products',
        verbose_name='Категории',
        blank=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Владелец товара'
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
        default=0
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (остаток: {self.number})"

    def is_in_stock(self):
        return self.number > 0

    is_in_stock.boolean = True


class Order(models.Model):
    """
    Модель заказа
    """

    class Status(models.TextChoices):
        NEW = 'new', 'Новый'
        SHIPPED = 'shipped', 'Отправлен'
        RETURNED = 'returned', 'Возврат'

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Пользователь'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Товар'
    )

    count = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1,
        validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата создания',
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='Статус',
        db_index=True
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Общая стоимость',
        default=0,
        editable=False
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Примечания'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"

    def save(self, *args, **kwargs):
        if self.product_id and self.count:
            self.total_price = self.product.price * self.count
        super().save(*args, **kwargs)
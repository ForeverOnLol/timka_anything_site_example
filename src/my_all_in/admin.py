from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile, Category, Product, Order


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'get_fio', 'get_role', 'get_phone', 'is_staff']
    list_select_related = ['profile']

    def get_fio(self, instance):
        return instance.profile.fio if hasattr(instance, 'profile') else '-'

    get_fio.short_description = 'ФИО'

    def get_role(self, instance):
        return instance.profile.get_role_display() if hasattr(instance, 'profile') else '-'

    get_role.short_description = 'Роль'

    def get_phone(self, instance):
        return instance.profile.phone if hasattr(instance, 'profile') else '-'

    get_phone.short_description = 'Телефон'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['fio', 'user', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['fio', 'user__username', 'user__email', 'phone']
    raw_id_fields = ['user']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'products_count', 'created_at']
    list_filter = ['user']
    search_fields = ['name']

    def products_count(self, obj):
        return obj.products.count()

    products_count.short_description = 'Товаров'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'price', 'number', 'is_active']
    list_filter = ['categories', 'is_active']
    search_fields = ['name', 'payload']
    list_editable = ['price', 'number', 'is_active']
    filter_horizontal = ['categories']
    raw_id_fields = ['user']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'count', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'product__name']
    list_editable = ['status']
    raw_id_fields = ['user', 'product']

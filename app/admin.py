
from django.apps import apps
from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.html import format_html

from app.models import (
    User,
    UserGroup,
    Vendor,
    AttributeValue, Attribute,
    Product, ProductVariant,
    Order, OrderItem,
    Cart, CartItem,
    Payment, PaymentMethod,
    Voucher, VoucherUsage,
)


class CartInline(admin.StackedInline):
    model = Cart
    extra = 0
    can_delete = False


class VendorInline(admin.StackedInline):
    model = Vendor
    extra = 0
    can_delete = False


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    show_change_link = True


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['attribute_value', 'price_modifier']
    show_change_link = True


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1
    fields = ['value']
    show_change_link = True


class VoucherUsageInline(admin.TabularInline):
    model = VoucherUsage
    extra = 1
    show_change_link = True


admin.site.unregister(Group)
@admin.register(UserGroup)
class CustomGroupAdmin(GroupAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'permissions',
            )
        }),
    )


@admin.register(User)
class UserAdmin(UserAdmin):
        
    class Meta:
        ordering = ('date_joined')

    inlines = [
        VendorInline,
        CartInline,
    ]

    fieldsets = (
        (None, {
            'fields': (
                'username',
                'password',
                'fullname',
                'email',
                'avatar',
                'address',
                'is_vendor',
            )
        }),
        ('Advanced options', {
            'classes': ('collapse'),
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        })
    )

    list_display = (
        'username',
        'fullname',
        'avatar_preview',
        'email',
        'view_vendor',
        'is_active',
        'is_vendor',
        'is_staff',
        'is_superuser',
    )

    list_filter = (
        'is_staff',
        'is_active',
        'is_vendor',
    )

    search_fields = (
        'username__startswith',
        'fullname__startswith',
    )
    
    def avatar_preview(self, obj):
        if obj.avatar:
            # avatar_url = obj.avatar.url
            # if avatar_url.__contains__('https'):
            #     avatar_url = obj.avatar
            return format_html(
                (
                    '<img src="{}"'
                    'style="width:50px; height:50px; border-radius:50%;" />'
                ),
                obj.avatar.url,
            )
        return "No Avatar"
    
    def view_vendor(self, obj):
        if obj.is_vendor:
            vendor = Vendor.objects.filter(user=obj).first()
            if vendor:
                url = f"/admin/app/vendor/{vendor.id}/change/"
                return mark_safe(f'<a href="{url}">{vendor.store_name}</a>')
        return None
    
    avatar_preview.short_description = 'Avatar'

    view_vendor.allow_tags = True
    view_vendor.short_description = 'Vendor Link'


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
    list_display = [
        'store_name',
        'user',
        'is_approved',
    ]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariantInline]
    list_display = [
        'name',
        'vendor',
        'category',
        'price',
    ]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = [
        'product',
        'attribute_value',
        'price_modifier',
    ]


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    inlines = [AttributeValueInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    inlines = [VoucherUsageInline]


for model in apps.get_app_config('app').get_models():
    try: admin.site.register(model)
    except: pass

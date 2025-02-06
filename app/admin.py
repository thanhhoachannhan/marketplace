
from django.apps import apps
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserChangeForm, ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.urls import reverse

from .models import *


class CartInline(admin.StackedInline):
    model = Cart
    extra = 0
    can_delete = False
    show_change_link = True

    def has_change_permission(self, request, obj=None):
        return False


class VendorInline(admin.StackedInline):
    model = Vendor
    extra = 0
    can_delete = True
    show_change_link = True
    readonly_fields = ['store_name', 'store_description']
    fields = ['store_name', 'store_description', 'is_approved']


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    show_change_link = True
    readonly_fields = ['description']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    readonly_fields = ['product_image_preview']
    fields = ['attribute_value', 'product_image_preview', 'price_modifier']
    show_change_link = True

    def product_image_preview(self, obj):
        if obj.image and obj.image.file and hasattr(obj.image.file, 'url'):
            return format_html(
                (
                    '<img src="{}"'
                    'style="width:50px; height:50px;" />'
                ),
                obj.image.file.url,
            )
        return _('NO IMAGE')

    product_image_preview.short_description = _('IMAGE')


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1
    fields = ['value']
    show_change_link = True


class VoucherUsageInline(admin.TabularInline):
    model = VoucherUsage
    extra = 0
    show_change_link = True
    
    def has_change_permission(self, request, obj=None):
        return False


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    readonly_fields = ['product_image_preview']
    fields = ['product_image_preview', 'is_default', 'rank']
    ordering = ['rank']
    show_change_link = True

    def product_image_preview(self, obj):
        if obj.file and hasattr(obj.file, 'url'):
            return format_html(
                (
                    '<img src="{}"'
                    'style="width:50px; height:50px;" />'
                ),
                obj.file.url,
            )
        return _('NO IMAGE')

    product_image_preview.short_description = _('FILE')


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

    
    class UserChangeForm(UserChangeForm):
        password = ReadOnlyPasswordHashField(
            label=_('PASSWORD'),
            help_text=_(
                'RAW PASSWORD NOT SAFE, YOU CAN CHANGE BY '
                '<a href=\'{}\'> FORM </a>.'
            ),
        )

    inlines = [
        VendorInline,
        CartInline,
    ]

    form = UserChangeForm

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
        (_('ADVANCED OPTIONS'), {
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
        'email__startswith',
    )
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                (
                    '<img src="{}"'
                    'style="width:50px; height:50px; border-radius:50%;" />'
                ),
                obj.avatar.url,
            )
        return _('NO AVATAR')
    
    def view_vendor(self, obj):
        if obj.is_vendor:
            vendor = Vendor.objects.filter(user=obj).first()
            if vendor:
                url = f'/admin/app/vendor/{vendor.id}/change/'
                return mark_safe(f'<a href="{url}">{vendor.store_name}</a>')
        return None
    
    avatar_preview.short_description = _('AVATAR')

    view_vendor.short_description = _('VENDOR')


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):

    inlines = [ProductInline]

    list_display = [
        'store_name',
        'user_link',
        'is_approved',
    ]

    list_filter = (
        'is_approved',
    )

    search_fields = (
        'store_name__startswith',
    )

    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:app_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = _('USER')
    user_link.admin_order_field = 'user'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = [
        'user',
        'vendor',
        'total_price',
        'is_paid',
        'status',
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    inlines = [
        ProductImageInline,
        ProductVariantInline,
    ]

    readonly_fields = [
        'default_image_preview',
    ]

    list_display = [
        'name',
        'default_image_preview',
        'vendor',
        'category',
        'price',
    ]

    def default_image_preview(self, obj):
        if obj.get_default_image():
            return format_html(
                (
                    '<img src="{}"'
                    'style="width:50px; height:50px;" />'
                ),
                obj.get_default_image().file.url,
            )
        return _('NO DEFAULT IMAGE')
    
    default_image_preview.short_description = _('DEFAULT IMAGE')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = [
        'product',
        'product_image_preview',
        'attribute_value',
        'price_modifier',
    ]

    def product_image_preview(self, obj):
        if obj.image and obj.image.file and hasattr(obj.image.file, 'url'):
            return format_html(
                (
                    '<img src="{}"'
                    'style="width:50px; height:50px;" />'
                ),
                obj.image.file.url,
            )
        return _('NO IMAGE')
    
    product_image_preview.short_description = _('IMAGE')


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    inlines = [AttributeValueInline]
    list_display = [
        'name',
    ]


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = [
        'attribute',
        'value',
    ]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    inlines = [VoucherUsageInline]


for model in apps.get_app_config('app').get_models():
    try: admin.site.register(model)
    except: pass

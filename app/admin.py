
from django.apps import apps
from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from app.models import User, UserGroup, Vendor


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


class VendorInline(admin.StackedInline):
    model = Vendor
    extra = 0
    can_delete = False


@admin.register(User)
class UserAdmin(UserAdmin):
        
    class Meta:
        ordering = ('date_joined')

    inlines = [VendorInline]

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
        'email',
        'is_vendor',
        'view_vendor',
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
    
    
    def view_vendor(self, obj):
        if obj.is_vendor:
            vendor = Vendor.objects.filter(user=obj).first()
            if vendor:
                url = f"/admin/app/vendor/{vendor.id}/change/"
                return mark_safe(f'<a href="{url}">{vendor.store_name}</a>')
        return None
    
    view_vendor.allow_tags = True
    view_vendor.short_description = 'Vendor Link'


for model in apps.get_app_config('app').get_models():
    try: admin.site.register(model)
    except: pass

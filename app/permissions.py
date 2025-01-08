from functools import wraps

from django.urls import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404

# from .models import (
#     Order,
# )


def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def is_marketplace_user(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'marketplaceuser'):
            return redirect(reverse('403'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def has_permission(permission_attr):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not getattr(request.user.marketplaceuser, permission_attr, False):
                return redirect(reverse('403'))
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def marketplace_superuser_required(view_func):
    @login_required
    @is_marketplace_user
    @has_permission('is_superuser')
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def marketplace_seller_required(view_func):
    @login_required
    @is_marketplace_user
    @has_permission('is_seller')
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def marketplace_buyer_required(view_func):
    @login_required
    @is_marketplace_user
    @has_permission('is_buyer')
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# def own_order_required(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, *args, **kwargs):
#         order_id = kwargs.get('order_id')

#         if kwargs.get('order_id'):
#             order = get_object_or_404(Order, id=order_id)
#             if order.buyer != request.user.marketplaceuser:
#                 return HttpResponseForbidden(
#                     "You can only view your own orders."
#                 )

#         return view_func(request, *args, **kwargs)

#     return _wrapped_view

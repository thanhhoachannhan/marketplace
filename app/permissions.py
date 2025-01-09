from functools import wraps

from django.urls import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from .models import *


def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(
                request,
                "You need to log in to access this page."
            )
            return redirect(f"{reverse('login')}?next={request.path}")
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
            if not getattr(request.user, permission_attr, False):
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


def own_order_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        order_id = kwargs.get('order_id')

        if kwargs.get('order_id'):
            order = get_object_or_404(Order, id=order_id)
            if order.user != request.user:
                return HttpResponseForbidden(
                    "You can only view your own orders."
                )

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def multi_ownership_required(ownership_rules):
    """
    ownership_rules:
        A dictionary mapping object_id_field -> (Model, user_field)

    Example:
        {
            'order_id': (Order, 'user'),
            'payment_id': (Payment, 'user')
        }
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            for object_id_field, (model, user_field) in ownership_rules.items():
                object_id = kwargs.get(object_id_field)
                if object_id:
                    obj = get_object_or_404(model, id=object_id)
                    if getattr(obj, user_field) != request.user:
                        return HttpResponseForbidden(
                            f"You do not have access to {model.__name__} "
                            f"with ID {object_id}."
                        )
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


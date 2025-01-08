
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    Permission, PermissionsMixin,
    UserManager, GroupManager,
)
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class UserGroup(models.Model):

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    objects = GroupManager()

    name = models.CharField(
        verbose_name = _('name'),
        max_length = 150,
        unique = True,
    )

    permissions = models.ManyToManyField(
        to = Permission,
        verbose_name = _('permissions'),
        blank = True,
    )

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


class User(AbstractBaseUser, PermissionsMixin):

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email']

    username = models.CharField(
        verbose_name = _('username'),
        max_length = 100,
        unique = True,
        validators = [
            UnicodeUsernameValidator(),
        ]
    )

    fullname = models.CharField(
        verbose_name = _('fullname'),
        max_length = 100,
        blank = True,
        null = True,
    )

    email = models.EmailField(
        verbose_name = _('email'),
        unique = True,
        blank = True,
        null = True,
    )

    avatar = models.ImageField(
        verbose_name = _('avatar'),
        upload_to = 'avatar',
        blank = True,
        null = True,
    )

    address = models.TextField(
        verbose_name = _('address'),
        blank = True,
        null = True,
    )

    is_staff = models.BooleanField(
        verbose_name = _('is_staff'),
        default = False,
    )

    is_active = models.BooleanField(
        verbose_name = _('is_active'),
        default = True,
    )

    date_joined = models.DateTimeField(
        verbose_name = _('date_joined'),
        default = timezone.now,
    )

    groups = models.ManyToManyField(
        to = UserGroup,
        verbose_name = _('groups'),
        blank = True,
    )

    is_vendor = models.BooleanField(
        verbose_name = _('is_vendor'),
        default = False,
    )

    def __str__(self):
        identity = self.fullname
        if not identity:
            identity = self.username 
        return identity


class Vendor(models.Model):

    user = models.ForeignKey(
        to = User,
        on_delete = models.CASCADE,
    )

    store_name = models.CharField(
        verbose_name = _('store_name'),
        max_length = 255,
    )

    store_description = models.TextField(
        blank = True,
        null = True,
    )

    is_approved = models.BooleanField(
        default = False
    )

    def __str__(self):
        return f'Vendor: {self.store_name} ( Own: {self.user} )'


class Category(models.Model):

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    name = models.CharField(
        verbose_name = 'category_name',
        max_length = 255,
    )

    parent = models.ForeignKey(
        to = 'self', 
        on_delete = models.CASCADE, 
        blank = True, 
        null = True, 
        related_name = 'children',
    )

    def __str__(self):
        parent_name = self.parent.name if self.parent else 'None'
        return f"{self.name} (Parent: {parent_name})"


class Product(models.Model):

    vendor = models.ForeignKey(
        to = Vendor,
        on_delete = models.CASCADE,
        related_name = 'products',
    )

    category = models.ForeignKey(
        to = Category,
        on_delete = models.SET_NULL,
        blank = True,
        null = True,
        related_name = 'products',
    )

    name = models.CharField(
        verbose_name = 'product_name',
        max_length = 255,
    )

    description = models.TextField(
        verbose_name = 'description',
        blank = True,
        null = True,
    )

    price = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
    )

    stock = models.PositiveIntegerField(
        default = 0,
    )

    is_active = models.BooleanField(
        default = True,
    )

    created_at = models.DateTimeField(
        auto_now_add = True,
    )
    updated_at = models.DateTimeField(
        auto_now = True,
    )

    def __str__(self):
        return f'Product: {self.name}'


class Attribute(models.Model):
    name = models.CharField(
        max_length = 255,
        unique = True,
    )

    def __str__(self):
        return self.name


class AttributeValue(models.Model):

    attribute = models.ForeignKey(
        to = Attribute,
        on_delete = models.CASCADE,
        related_name = "values",
    )

    value = models.CharField(
        max_length = 255,
    )

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductVariant(models.Model):

    product = models.ForeignKey(
        to = Product,
        on_delete = models.CASCADE,
        related_name = 'variants',
    )

    attribute_value = models.ForeignKey(
        to = AttributeValue,
        related_name = "variants",
        on_delete = models.CASCADE,
    )

    price_modifier = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
        default = 0,
    )

    def __str__(self):
        return (
            f'Variant: {self.product.name} '
            f'( {self.attribute_value.attribute.name} : '
            f'{self.attribute_value.value} )'
        )


class Cart(models.Model):

    user = models.ForeignKey(
        to = User,
        on_delete = models.CASCADE,
        related_name = 'carts',
    )

    vendor = models.ForeignKey(
        to = Vendor,
        on_delete = models.CASCADE,
        related_name = 'carts',
    )

    created_at = models.DateTimeField(
        auto_now_add = True,
    )

    updated_at = models.DateTimeField(
        auto_now = True,
    )

    def __str__(self):
        return f'Cart ( User: {self.user} | Vendor: {self.vendor} )'


class CartItem(models.Model):

    cart = models.ForeignKey(
        to = Cart,
        on_delete = models.CASCADE,
        related_name = 'items',
    )

    product = models.ForeignKey(
        to = Product,
        on_delete = models.CASCADE,
    )

    variant = models.ForeignKey(
        to = ProductVariant,
        on_delete = models.SET_NULL,
        null = True,
        blank = True,
    )

    quantity = models.PositiveIntegerField(
        default = 1,
    )

    def __str__(self):
        return f'CartItem: {self.product} ( Cart: {self.cart} )'

    def clean(self):
        if self.cart.vendor != self.product.vendor:
            raise ValidationError(
                "The product's vendor does not match the cart's vendor."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Order(models.Model):

    user = models.ForeignKey(
        to = User,
        on_delete = models.CASCADE,
        related_name = 'orders',
    )

    total_price = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
    )

    is_paid = models.BooleanField(
        default = False,
    )

    status = models.CharField(
        max_length = 20,
        choices = (
            ('Pending', 'Pending'),
            ('Processing', 'Processing'), 
            ('Shipped', 'Shipped'),
            ('Delivered', 'Delivered'),
            ('Cancelled', 'Cancelled'),
        ),
        default = 'Pending',
    )

    created_at = models.DateTimeField(
        auto_now_add = True,
    )

    updated_at = models.DateTimeField(
        auto_now = True,
    )
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, 
                              related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, 
                                null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    def total_paid(self):
        return sum(payment.amount for payment in self.payments.all())

    def remaining_amount(self):
        return self.total_amount - self.total_paid()

    def is_fully_paid(self):
        return self.remaining_amount() <= 0

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.CharField(max_length=50, choices=(
        ('Credit Card', 'Credit Card'), ('PayPal', 'PayPal'), 
        ('Bank Transfer', 'Bank Transfer')))
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(
        ('Pending', 'Pending'), ('Completed', 'Completed'), 
        ('Failed', 'Failed')), default='Pending')

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
        return f'{self.store_name} ( Own: {self.user} )'


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


class ProductImage(models.Model):

    product = models.ForeignKey(
        to = Product,
        on_delete = models.CASCADE,
        related_name = 'images',
        verbose_name = _('product'),
    )

    file = models.ImageField(
        verbose_name = _('image'),
        upload_to = 'product_images/',
        blank = True,
        null = True,
    )

    is_default = models.BooleanField(
        verbose_name = _('is default'),
        default = False,
    )

    rank = models.PositiveIntegerField(
        verbose_name = _('rank'),
        default = 0,
        help_text = _('The rank of the image. Smaller numbers appear first.'),
    )

    created_at = models.DateTimeField(
        auto_now_add = True,
        verbose_name = _('created at'),
    )

    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')
        ordering = ['rank', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name} (Rank: {self.rank})"

    def clean(self):
        if self.is_default:
            # Đảm bảo chỉ có một ảnh mặc định cho mỗi sản phẩm
            ProductImage.objects.filter(
                product=self.product, is_default=True
            ).exclude(id=self.id).update(is_default=False)


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

    image = models.ForeignKey(
        to = ProductImage,
        on_delete = models.SET_NULL,
        blank = True,
        null = True,
        related_name = "variant_images",
        verbose_name = _('variant image'),
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
    
    def get_image(self):
        """Return the image for the variant or the default product image."""
        if self.image:
            return self.image.image.url
        default_image = self.product.images.filter(is_default=True).first()
        return default_image.image.url if default_image else None
    

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

    vendor = models.ForeignKey(
        to = Vendor,
        on_delete = models.CASCADE,
        related_name = 'orders',
    )

    total_price = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
        blank = True,
        null = True,
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

    def calculate_total_price(self):
        """
        Recalculate the total price of the order based on its items.
        """
        try:
            if self.pk is None:
                return

            total = sum(
                item.quantity * item.price
                for item in self.orderitem_set.all()
            )
            self.total_price = total

            self.save()

        except Exception as ex:
            print(ex)

    def __str__(self):
        return (
            f'Order: {self.id} - ${self.total_price} '
            f'( User: {self.user} - Vendor: {self.vendor} )'
        )


class OrderItem(models.Model):

    order = models.ForeignKey(
        to=Order,
        on_delete=models.CASCADE,
        related_name='orderitem_set',
    )
    
    product = models.ForeignKey(
        to = Product,
        on_delete = models.CASCADE,
    )

    variant = models.ForeignKey(
        to = ProductVariant,
        on_delete = models.SET_NULL,
        blank = True,
        null = True,
    )

    quantity = models.PositiveIntegerField(
        default = 1,
    )

    price = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
        blank = True,
        null = True,
    )

    def __str__(self):
        return f'OrderItem: {self.product} ( Variant: {self.variant} )'

    def calculate_price(self):
        """
        Calculate the price for this item, considering variant modifiers.
        """
        base_price = self.product.price
        variant_modifier = self.variant.price_modifier if self.variant else 0
        self.price = base_price + variant_modifier

        self.save()


class PaymentMethod(models.Model):

    name = models.CharField(
        max_length = 50,
        choices = [
            ('Credit Card', 'Credit Card'),
            ('PayPal', 'PayPal'),
            ('Bank Transfer', 'Bank Transfer'),
        ],
    )

    description = models.TextField(
        blank = True,
        null = True,
    )

    def __str__(self):
        return self.name


class Voucher(models.Model):

    code = models.CharField(
        max_length = 20,
        unique = True,
    )

    discount_amount = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
    )

    payment_method = models.ForeignKey(
        to = PaymentMethod,
        on_delete = models.SET_NULL,
        blank = True,
        null = True,
    )

    minimum_order_value = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
        default = 0,
    )

    expiry_date = models.DateTimeField()

    def is_valid(self, order_total):
        return (
            self.expiry_date >= timezone.now() and
            order_total >= self.minimum_order_value
        )

    def __str__(self):
        return f"Voucher {self.code} - ${self.discount_amount}"


class Payment(models.Model):

    order = models.ForeignKey(
        to = Order,
        on_delete = models.CASCADE,
        related_name = 'payments',
    )
    
    payment_method = models.ForeignKey(
        to = PaymentMethod,
        on_delete = models.CASCADE,
    )

    amount = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
        blank = True,
        null = True,
    )

    payment_date = models.DateTimeField(
        auto_now_add = True,
    )

    status = models.CharField(
        max_length = 20,
        choices = [
            ('Pending', 'Pending'),
            ('Completed', 'Completed'),
            ('Failed', 'Failed'),
        ],
        default = 'Pending',
    )

    def calculate_payment_amount(self):
        """
        Calculate the payment amount after applying any valid vouchers.
        """
        try:
            if self.pk is None:
                return

            order_total = self.order.total_price

            total_discount = sum(
                usage.voucher.discount_amount
                for usage in self.voucherusage_set.all()
                if usage.voucher.is_valid(order_total)
            )

            self.amount = max(order_total - total_discount, 0)

            self.save()

        except Exception as ex:
            print(ex)


    def __str__(self):
        return (
            f'Payment for Order #{self.order.id} '
            f'- ${self.amount} - {self.payment_method}'
        )


class VoucherUsage(models.Model):

    voucher = models.ForeignKey(
        to = Voucher,
        on_delete = models.CASCADE,
        related_name = "voucherusage_set",
    )

    payment = models.ForeignKey(
        to = Payment,
        on_delete = models.CASCADE,
        related_name = "voucherusage_set",
    )

    applied_amount = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
        default = 0,
    )

    created_at = models.DateTimeField(
        auto_now_add = True,
    )

    def clean(self):
        if self.applied_amount < 0:
            raise ValidationError("Applied amount cannot be negative.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


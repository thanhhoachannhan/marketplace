
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
        verbose_name = _('GROUP')
        verbose_name_plural = _('USER_GROUP')

    objects = GroupManager()

    name = models.CharField(
        verbose_name = _('NAME'),
        max_length = 150,
        unique = True,
    )

    permissions = models.ManyToManyField(
        to = Permission,
        verbose_name = _('PERMISSIONS'),
        blank = True,
    )

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


class User(AbstractBaseUser, PermissionsMixin):

    class Meta:
        verbose_name = _('USER')
        verbose_name_plural = _('USERS')

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email']

    username = models.CharField(
        verbose_name = _('USERNAME'),
        max_length = 100,
        unique = True,
        validators = [
            UnicodeUsernameValidator(),
        ]
    )

    fullname = models.CharField(
        verbose_name = _('FULLNAME'),
        max_length = 100,
        blank = True,
        null = True,
    )

    email = models.EmailField(
        verbose_name = _('EMAIL'),
        unique = True,
        blank = True,
        null = True,
    )

    avatar = models.ImageField(
        verbose_name = _('AVATAR'),
        upload_to = 'avatar',
        blank = True,
        null = True,
    )

    address = models.TextField(
        verbose_name = _('ADDRESS'),
        blank = True,
        null = True,
    )

    is_staff = models.BooleanField(
        verbose_name = _('IS_STAFF'),
        default = False,
    )

    is_active = models.BooleanField(
        verbose_name = _('IS_ACTIVE'),
        default = True,
    )

    date_joined = models.DateTimeField(
        verbose_name = _('DATE_JOINED'),
        default = timezone.now,
    )

    groups = models.ManyToManyField(
        to = UserGroup,
        verbose_name = _('GROUPS'),
        blank = True,
    )

    is_vendor = models.BooleanField(
        verbose_name = _('IS_VENDOR'),
        default = False,
    )

    def __str__(self):
        identity = self.fullname
        if not identity:
            identity = self.username 
        return identity


class Vendor(models.Model):

    class Meta:
        verbose_name = _('VENDOR')
        verbose_name_plural = _('VENDORS')

    user = models.ForeignKey(
        to = User,
        verbose_name = _('USER'),
        on_delete = models.CASCADE,
        # related_name = 'vendor_set',
    )

    store_name = models.CharField(
        verbose_name = _('STORE_NAME'),
        max_length = 255,
    )

    store_description = models.TextField(
        verbose_name = _('DESCRIPTION'),
        blank = True,
        null = True,
    )

    is_approved = models.BooleanField(
        verbose_name = _('IS_APPROVED'),
        default = False
    )

    def __str__(self):
        return ('{} [{}: {}]').format(
            self.store_name,
            _("OWN"),
            self.user,
        )


class Category(models.Model):

    class Meta:
        verbose_name = _('CATEGORY')
        verbose_name_plural = _('CATEGORIES')

    name = models.CharField(
        verbose_name = _('NAME'),
        max_length = 255,
    )

    parent = models.ForeignKey(
        to = 'self',
        verbose_name = _('PARENT'),
        on_delete = models.CASCADE, 
        blank = True, 
        null = True, 
        # related_name = 'category_set',
    )

    def __str__(self):

        parent_name = _('NONE')
        if self.parent:
            parent_name = self.parent.name

        return ('{} [{}: {}]').format(
            self.name,
            _('PARENT'),
            parent_name,
        )


class Product(models.Model):

    class Meta:
        verbose_name = _('PRODUCT')
        verbose_name_plural = _('PRODUCTS')

    vendor = models.ForeignKey(
        to = Vendor,
        verbose_name = _('VENDOR'),
        on_delete = models.CASCADE,
        # related_name = 'product_set',
    )

    category = models.ForeignKey(
        to = Category,
        verbose_name = _('CATEGORY'),
        on_delete = models.SET_NULL,
        blank = True,
        null = True,
        # related_name = 'product_set',
    )

    name = models.CharField(
        verbose_name = _('NAME'),
        max_length = 255,
    )

    description = models.TextField(
        verbose_name = _('DESCRIPTION'),
        blank = True,
        null = True,
    )

    price = models.DecimalField(
        verbose_name = _('PRICE'),
        max_digits = 10,
        decimal_places = 2,
    )

    stock = models.PositiveIntegerField(
        verbose_name = _('STOCK'),
        default = 0,
    )

    is_active = models.BooleanField(
        verbose_name = _('IS_ACTIVE'),
        default = True,
    )

    created_at = models.DateTimeField(
        verbose_name = _('CREATED_AT'),
        auto_now_add = True,
    )
    updated_at = models.DateTimeField(
        verbose_name = _('UPDATED_AT'),
        auto_now = True,
    )

    def __str__(self):
        return ('{}: {}').format(
            _('PRODUCT'),
            self.name,
        )

    def get_default_image(self):
        default_image = self.productimage_set.filter(
            is_default = True,
        ).first()
        return default_image


class Attribute(models.Model):

    class Meta:
        verbose_name = _('ATTRIBUTE')
        verbose_name_plural = _('ATTRIBUTES')

    name = models.CharField(
        verbose_name = _('NAME'),
        max_length = 255,
        unique = True,
    )

    def __str__(self):
        return self.name


class AttributeValue(models.Model):

    class Meta:
        verbose_name = _('ATTRIBUTE_VALUE')
        verbose_name_plural = _('ATTRIBUTE_VALUES')

    attribute = models.ForeignKey(
        verbose_name = _('ATTRIBUTE'),
        to = Attribute,
        on_delete = models.CASCADE,
        # related_name = 'attributevalue_set',
    )

    value = models.CharField(
        verbose_name = _('VALUE'),
        max_length = 255,
    )

    def __str__(self):
        return ('{}: {}').format(
            self.attribute.name,
            self.value,
        )


class ProductImage(models.Model):

    class Meta:
        verbose_name = _('PRODUCT_IMAGE')
        verbose_name_plural = _('PRODUCT_IMAGES')
        ordering = ['rank', 'created_at']

    product = models.ForeignKey(
        to = Product,
        verbose_name = _('PRODUCT'),
        on_delete = models.CASCADE,
        # related_name = 'productimage_set',
    )

    file = models.ImageField(
        verbose_name = _('FILE'),
        upload_to = 'product_images/',
        blank = True,
        null = True,
    )

    is_default = models.BooleanField(
        verbose_name = _('IS_DEFAULT'),
        default = False,
    )

    rank = models.PositiveIntegerField(
        verbose_name = _('RANK'),
        default = 0,
        help_text = _('THE_RANK_OF_IMAGE'),
    )

    created_at = models.DateTimeField(
        verbose_name = _('CREATED_AT'),
        auto_now_add = True,
    )

    def __str__(self):
        return ('{} ({}:{} - {}: {})').format(
            _('IMAGE'),
            _('PRODUCT'),
            self.product.name,
            _('RANK'),
            self.rank,
        )

    def clean(self):
        '''
            Make sure only one default image for product.
        '''
        if self.is_default:
            ProductImage.objects.filter(
                product=self.product, is_default=True
            ).exclude(id=self.id).update(is_default=False)


class ProductVariant(models.Model):

    class Meta:
        verbose_name = _('PRODUCT_VARIANT')
        verbose_name_plural = _('PRODUCT_VARIANTS')

    product = models.ForeignKey(
        to = Product,
        verbose_name = _('PRODUCT'),
        on_delete = models.CASCADE,
        # related_name = 'productvariant_set',
    )

    attribute_value = models.ForeignKey(
        to = AttributeValue,
        verbose_name = _('ATTRIBUTE_VALUE'),
        # related_name = 'productvariant_set',
        on_delete = models.CASCADE,
    )

    image = models.ForeignKey(
        to = ProductImage,
        verbose_name = _('IMAGE'),
        on_delete = models.SET_NULL,
        blank = True,
        null = True,
        # related_name = 'productvariant_set',
    )

    price_modifier = models.DecimalField(
        verbose_name = _('PRICE_MODIFIER'),
        max_digits = 10,
        decimal_places = 2,
        default = 0,
    )

    def __str__(self):
        return ('{}: {} [{}: {}]').format(
            _('PRODUCT_VARIANT'),
            self.product.name,
            self.attribute_value.attribute.name,
            self.attribute_value.value,
        )
    
    def get_image(self):
        '''
            Return the image for the variant or the default product image.
        '''
        if self.image:
            return self.image.image.url
        default_image = self.product.images.filter(is_default=True).first()
        return default_image.image.url if default_image else None
    

class Cart(models.Model):

    class Meta:
        verbose_name = _('CART')
        verbose_name_plural = _('CARTS')

    user = models.ForeignKey(
        to = User,
        on_delete = models.CASCADE,
        # related_name = 'cart_set',
    )

    vendor = models.ForeignKey(
        to = Vendor,
        verbose_name = _('VENDOR'),
        on_delete = models.CASCADE,
        # related_name = 'cart_set',
    )

    created_at = models.DateTimeField(
        verbose_name = _('CREATED_AT'),
        auto_now_add = True,
    )

    updated_at = models.DateTimeField(
        verbose_name = _('UPDATED_AT'),
        auto_now = True,
    )

    def __str__(self):
        return ('{} [{}: {} - {}: {}]').format(
            _('CART'),
            _('USER'),
            self.user,
            _('VENDOR'),
            self.vendor,
        )


class CartItem(models.Model):

    class Meta:
        verbose_name = _('CART_ITEM')
        verbose_name_plural = _('CART_ITEMS')

    cart = models.ForeignKey(
        to = Cart,
        verbose_name = _('CART'),
        on_delete = models.CASCADE,
        # related_name = 'cartitem_set',
    )

    product = models.ForeignKey(
        to = Product,
        verbose_name = _('PRODUCT'),
        on_delete = models.CASCADE,
        # related_name = 'cartitem_set',
    )

    variant = models.ForeignKey(
        to = ProductVariant,
        verbose_name = _('PRODUCT_VARIANT'),
        on_delete = models.SET_NULL,
        null = True,
        blank = True,
        # related_name = 'cartitem_set',
    )

    quantity = models.PositiveIntegerField(
        default = 1,
    )

    def __str__(self):
        return f'CartItem: {self.product} ( Cart: {self.cart} )'

    def clean(self):
        if self.cart.vendor != self.product.vendor:
            raise ValidationError(
                'The product\'s vendor does not match the cart\'s vendor.'
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Order(models.Model):

    user = models.ForeignKey(
        to = User,
        on_delete = models.CASCADE,
        # related_name = 'order_set',
    )

    vendor = models.ForeignKey(
        to = Vendor,
        on_delete = models.CASCADE,
        # related_name = 'order_set',
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
        '''
        Recalculate the total price of the order based on its items.
        '''
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
        # related_name='orderitem_set',
    )
    
    product = models.ForeignKey(
        to = Product,
        on_delete = models.CASCADE,
        # related_name='orderitem_set',
    )

    variant = models.ForeignKey(
        to = ProductVariant,
        on_delete = models.SET_NULL,
        blank = True,
        null = True,
        # related_name='orderitem_set',
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
        '''
        Calculate the price for this item, considering variant modifiers.
        '''
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
        # related_name='voucher_set',
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
        return f'Voucher {self.code} - ${self.discount_amount}'


class Payment(models.Model):

    order = models.ForeignKey(
        to = Order,
        on_delete = models.CASCADE,
        # related_name = 'payment_set',
    )
    
    payment_method = models.ForeignKey(
        to = PaymentMethod,
        on_delete = models.CASCADE,
        # related_name = 'payment_set',
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
        '''
        Calculate the payment amount after applying any valid vouchers.
        '''
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
        # related_name = 'voucherusage_set',
    )

    payment = models.ForeignKey(
        to = Payment,
        on_delete = models.CASCADE,
        # related_name = 'voucherusage_set',
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
            raise ValidationError('Applied amount cannot be negative.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


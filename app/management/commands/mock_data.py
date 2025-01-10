
import random, requests

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db import transaction

from faker import Faker

from app.models import *


RECORD = 3
MAX_DEPTH = 3
PASSWORD = 'test'

faker = Faker()

class Command(BaseCommand):
    help = 'Create mock data for testing'

    def handle(self, *args, **kwargs):

        def random_boolean(true_weight=0.5, false_weight=0.5):
            return random.choices(
                population = [True, False],
                weights = [true_weight, false_weight],
                k = 1,
            )[0]
        
        def random_user_and_vendor():
            for _ in range(RECORD):
                user = User.objects.create_user(

                    username = faker.user_name(),
                    password = PASSWORD,

                    email = faker.email(),
                    fullname = faker.name(),
                    address = faker.address(),

                    is_vendor = random_boolean(),
                )

                avatar_url = faker.image_url(
                    placeholder_url = 'https://picsum.photos/{width}/{height}'
                )

                try:
                    response = requests.get(avatar_url)
                    user.avatar.save(
                        f"{faker.uuid4()}.jpg",
                        ContentFile(response.content),
                        save=True,
                    )
                except Exception as ex:
                    self.stdout.write(
                        self.style.ERROR(ex),
                    )

                if user.is_vendor:
                    Vendor.objects.create(
                        user = user,
                        store_name = faker.company(),
                        store_description = faker.text(),
                        is_approved = random_boolean(),
                    )

            self.stdout.write(
                self.style.SUCCESS('User & Vendor created successfully!'),
            )
        
        def random_category_tree():

            def get_depth(category):
                depth = 0
                while category.parent:
                    depth += 1
                    category = category.parent
                return depth
            
            categories = []

            for _ in range(RECORD):

                possible_parents = [
                    category for category in categories
                    if get_depth(category) < MAX_DEPTH
                ]

                parent = None

                if possible_parents and random.random() > 0.3:
                    parent = random.choice(possible_parents)

                category = Category.objects.create(
                    name=faker.word().capitalize(),
                    parent=parent
                )
                categories.append(category)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {len(categories)} categories '
                    f'with up to {MAX_DEPTH} levels!'
                )
            )

            return categories

        def random_attributes_and_values():

            attributes = []

            for _ in range(RECORD):

                attribute = Attribute.objects.create(
                    name = faker.word().capitalize(),
                )

                for _ in range(RECORD):

                    AttributeValue.objects.create(
                        attribute=attribute,
                        value=faker.word().capitalize(),
                    )

                attributes.append(attribute)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {len(attributes)} attributes and their values!'
                )
            )

        def random_products():
            vendors = Vendor.objects.all()
            categories = Category.objects.all()

            if not vendors:
                raise ValueError(
                    "No vendors were created. "
                    "Ensure some users are vendors."
                )

            products = []

            for vendor in vendors:

                num_products = random.randint(1, RECORD)

                for _ in range(num_products):

                    category = random.choice(categories)

                    product = Product.objects.create(
                        vendor = vendor,
                        category = category,
                        name = faker.word().capitalize(),
                        description = faker.text(),
                        price = round(random.uniform(10, 500), 2),
                        stock = random.randint(1, 100),
                    )

                    products.append(product)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {len(products)} products '
                    f'for {len(vendors)} vendors!'
                )
            )

            return products

        def random_product_images():
            products = Product.objects.all()
            images = []

            for product in products:
                num_images = random.randint(1, RECORD)
                for i in range(num_images):
                    image = ProductImage.objects.create(
                        product = product,
                        is_default = (i == 0),
                        rank = i + 1,
                    )
                    product_image_url = faker.image_url(
                        placeholder_url = (
                            'https://picsum.photos/{width}/{height}'
                        )
                    )
                    try:
                        response = requests.get(product_image_url)
                        image.file.save(
                            f"{faker.uuid4()}.jpg",
                            ContentFile(response.content),
                            save=True,
                        )
                    except Exception as ex:
                        self.stdout.write(
                            self.style.ERROR(ex),
                        )

                    images.append(image)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {len(images)} product images '
                    f'for {len(products)} products!'
                )
            )


        def random_product_variants():

            products = Product.objects.all()

            attribute_values = list(AttributeValue.objects.all())

            for product in products:

                product_images = ProductImage.objects.filter(
                    product = product,
                    is_default = False,
                )

                variants = set()

                for _ in range(random.randint(1, RECORD)):

                    value = random.choice(attribute_values)

                    if value in variants:
                        continue
                    variants.add(value)

                    image = None
                    if product_images:
                        image = random.choice(product_images)

                    ProductVariant.objects.create(
                        product = product,
                        attribute_value = value,
                        image = image,
                        price_modifier = round(random.uniform(0, 50), 2),
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created variants for {len(products)} products!'
                )
            )

        def random_carts():

            users = User.objects.filter(is_vendor=False)
            vendors = Vendor.objects.all()

            carts = []

            for user in users:

                num_vendors = random.randint(1, len(vendors))
                selected_vendors = random.sample(
                    population = list(vendors),
                    k = num_vendors,
                )

                for vendor in selected_vendors:

                    cart = Cart.objects.create(
                        user = user,
                        vendor = vendor,
                    )

                    carts.append(cart)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {len(carts)} carts across {len(users)} users!'
                )
            )

            return carts
        
        def random_cart_items():

            carts = Cart.objects.all()
            products = Product.objects.all()

            cart_items = []

            for cart in carts:

                vendor_products = products.filter(
                    vendor = cart.vendor,
                )

                if not vendor_products:
                    self.stdout.write(
                        self.style.ERROR(
                            f'cart.vendor: {cart.vendor} \n'
                            f'cart.vendor: {cart.vendor} \n'
                        )
                    )
                    continue

                num_items = random.randint(1, 5)

                for _ in range(num_items):
                    
                    product = random.sample(
                        population = list(vendor_products),
                        k = 1,
                    )[0]

                    variant = None
                    if product.variants.exists():
                        variant = random.sample(
                            population = list(product.variants.all()),
                            k = 1,
                        )[0]

                    quantity = random.randint(1, 10)

                    cart_item = CartItem.objects.create(
                        cart = cart,
                        product = product,
                        variant = variant,
                        quantity = quantity,
                    )

                    cart_items.append(cart_item)

            self.stdout.write(
                self.style.SUCCESS(f'Created {len(cart_items)} cart items!')
            )

        def random_orders():
            
            users = User.objects.filter(is_vendor=False)
            vendors = Vendor.objects.all()

            orders = []

            for user in users:

                num_vendors = random.randint(1, len(vendors))
                selected_vendors = random.sample(
                    population = list(vendors),
                    k = num_vendors,
                )

                for vendor in selected_vendors:

                    order = Order.objects.create(
                        user = user,
                        vendor = vendor,
                    )

                    orders.append(order)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {len(orders)} orders across {len(users)} users!'
                )
            )

            return orders

        def random_order_items():
            
            orders = Order.objects.all()
            products = Product.objects.all()

            order_items = []

            for order in orders:

                vendor_products = products.filter(
                    vendor = order.vendor,
                )

                if not vendor_products:
                    continue

                num_items = random.randint(1, 5)

                order_products_added = set()

                for _ in range(num_items):
                    
                    product = random.sample(
                        population = list(vendor_products),
                        k = 1,
                    )[0]

                    variant = None
                    if product.variants.exists():
                        variant = random.sample(
                            population = list(product.variants.all()),
                            k = 1,
                        )[0]
                    
                    if (product, variant) in order_products_added:
                        continue
                    order_products_added.add((product, variant))

                    quantity = random.randint(1, 10)

                    order_item = OrderItem.objects.create(
                        order = order,
                        product = product,
                        variant = variant,
                        quantity = quantity,
                    )

                    order_item.calculate_price()
                    order_item.order.calculate_total_price()

                    order_items.append(order_item)

            self.stdout.write(
                self.style.SUCCESS(f'Created {len(order_items)} order items!')
            )

        def random_payment_methods():

            payment_methods = [
                'Credit Card',
                'PayPal',
                'Bank Transfer',
            ]

            for method in payment_methods:

                PaymentMethod.objects.create(
                    name = method,
                    description = f"Payment method {method} description",
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {len(payment_methods)} payment methods!'
                )
            )

        def random_voucher():

            payment_methods = list(PaymentMethod.objects.all())
            payment_methods.append(None)

            vouchers = []

            for _ in range(RECORD):

                voucher = Voucher.objects.create(
                    code = faker.uuid4()[:8].upper(),
                    discount_amount = round(random.uniform(5, 50), 2),
                    payment_method = random.choice(payment_methods),
                    minimum_order_value = round(random.uniform(50, 200), 2),
                    expiry_date = faker.future_date(end_date='+30d'),
                )

                vouchers.append(voucher)

            self.stdout.write(
                self.style.SUCCESS(f'Created {len(vouchers)} vouchers!')
            )

        def random_payments():

            orders = Order.objects.all()
            payment_methods = list(PaymentMethod.objects.all())

            payments = []
            
            for order in orders:
                payment_method = random.choice(payment_methods)

                payment = Payment.objects.create(
                    order = order,
                    payment_method = payment_method,
                    status = random.choice([
                        'Pending',
                        'Completed',
                        'Failed',
                    ]),
                )

                payments.append(payment)

            self.stdout.write(
                self.style.SUCCESS(f'Created {len(payments)} payments!')
            )

        def random_voucher_usage():

            payments = Payment.objects.all()
            vouchers = list(Voucher.objects.all())

            voucher_usages = []

            for payment in payments:

                num_vouchers = random.randint(1, min(len(vouchers), 3))
                selected_vouchers = random.sample(vouchers, num_vouchers)

                for voucher in selected_vouchers:

                    voucher_usage = VoucherUsage.objects.create(
                        voucher = voucher,
                        payment = payment,
                    )


                    voucher_usages.append(voucher_usage)

                payment.calculate_payment_amount()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {len(voucher_usages)} voucher usages!'
                )
            )

        try:
            with transaction.atomic():

                random_user_and_vendor()

                random_category_tree()

                random_attributes_and_values()

                random_products()

                random_product_images()

                random_product_variants()

                random_carts()
                
                random_cart_items()

                random_orders()

                random_order_items()

                random_payment_methods()

                random_voucher()

                random_payments()

                random_voucher_usage()

                self.stdout.write(
                    self.style.SUCCESS(
                        "Mock data created successfully!"
                    )
                )
        
        except Exception as ex:
            transaction.rollback()
            print(ex)



import random

from django.core.management.base import BaseCommand
from django.db import transaction

from faker import Faker

from app.models import (
    User,
    Vendor,
    Category,
    Product,
    Attribute,
    AttributeValue,
    ProductVariant,
)


RECORD = 10
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

        def random_products(categories, vendors):

            products = []

            for _ in range(RECORD):

                vendor = random.choice(vendors)
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
                self.style.SUCCESS(f'Created {len(products)} products!')
            )

            return products

        def random_product_variants(products):

            attribute_values = AttributeValue.objects.all()

            for product in products:

                variants = set()

                for _ in range(random.randint(1, RECORD)):

                    value = random.choice(attribute_values)
                    if value in variants:
                        continue
                    variants.add(value)

                    ProductVariant.objects.create(
                        product=product,
                        attribute_value=value,
                        price_modifier=round(random.uniform(0, 50), 2),
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created variants for {len(products)} products!'
                )
            )

        try:
            with transaction.atomic():

                random_user_and_vendor()

                categories = random_category_tree()

                random_attributes_and_values()

                vendors = list(Vendor.objects.all())

                if not vendors:
                    raise ValueError(
                        "No vendors were created. "
                        "Ensure some users are vendors."
                    )

                products = random_products(categories, vendors)

                random_product_variants(products)

                self.stdout.write(
                    self.style.SUCCESS("Mock data created successfully!")
                )
        
        except Exception as ex:
            transaction.rollback()
            print(ex)


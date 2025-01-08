
import random

from django.core.management.base import BaseCommand
from django.db import transaction

from faker import Faker

from app.models import (
    User,
    Vendor,
    Category,
    Product,
    ProductVariant,
)


RECORD = 5
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
        
        try:
            with transaction.atomic():
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
                    self.style.SUCCESS('Mock data created successfully!'),
                )
                self.stdout.write(
                    self.style.SUCCESS(faker.image_url()),
                )
        
        except Exception as ex:
            transaction.rollback()
            print(ex)


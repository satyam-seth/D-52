from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from records.models import Electricity, Maid, Record, Water

User = get_user_model()


class RecordModelTest(TestCase):
    """Test Record Model"""

    def setUp(self) -> None:
        self.adder = User.objects.create(
            username="test-user-1", password="test-password-1"
        )
        self.purchaser = User.objects.create(
            username="test-user-2", password="test-password-2"
        )

    def test_record_creation(self) -> None:
        """Test record model instance creation"""

        # initialize data
        item = "test-item"
        price = 99.99
        purchase_date = timezone.now().date()

        # create record instance
        record = Record.objects.create(
            item=item,
            price=price,
            purchaser=self.purchaser,
            adder=self.adder,
            purchase_date=purchase_date,
        )

        # assert field values
        self.assertEqual(record.item, item)
        self.assertEqual(record.price, price)
        self.assertEqual(record.purchaser, self.purchaser)
        self.assertEqual(record.adder, self.adder)
        self.assertEqual(record.purchase_date, purchase_date)
        # TODO: add assertion for modified_on field and created_on
        # self.assertEqual(record.created_on, timezone.now())

        # assert string representation
        self.assertEqual(str(record), f"{record.item} {record.purchaser.username}")


class WaterModelTest(TestCase):
    """Test Water Model"""

    def setUp(self) -> None:
        self.adder = User.objects.create(username="test-user", password="test-password")

    def test_water_creation(self) -> None:
        """Test water model instance creation"""

        # initialize data
        quantity = 1
        purchase_date = timezone.now().date()

        # create water instance
        water = Water.objects.create(
            quantity=quantity,
            adder=self.adder,
            purchase_date=purchase_date,
        )

        # assert field values
        self.assertEqual(water.quantity, quantity)
        self.assertEqual(water.adder, self.adder)
        self.assertEqual(water.purchase_date, purchase_date)
        # TODO: add assertion for modified_on field and created_on

        # assert string representation
        self.assertEqual(str(water), str(water.purchase_date))


class ElectricityModelTest(TestCase):
    """Test Electricity Model"""

    def test_electricity_creation(self) -> None:
        """Test electricity model instance creation"""

        # initialize data
        price = 1234
        due_date = timezone.now().date()

        # create electricity instance
        electricity = Electricity.objects.create(
            price=price,
            due_date=due_date,
        )

        # assert field values
        self.assertEqual(electricity.price, price)
        self.assertEqual(electricity.due_date, due_date)
        # TODO: add assertion for modified_on field and created_on

        # assert string representation
        self.assertEqual(str(electricity), str(electricity.due_date))


class MaidModelTest(TestCase):
    """Test Maid Model"""

    def test_maid_creation(self) -> None:
        """Test maid model instance creation"""

        # initialize data
        price = 5678
        due_date = timezone.now().date()

        # create maid instance
        maid = Maid.objects.create(
            price=price,
            due_date=due_date,
        )

        # assert field values
        self.assertEqual(maid.price, price)
        self.assertEqual(maid.due_date, due_date)
        # TODO: add assertion for modified_on field and created_on

        # assert string representation
        self.assertEqual(str(maid), str(maid.due_date))

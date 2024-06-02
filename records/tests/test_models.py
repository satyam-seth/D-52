from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from accounts.models import Room, RoomMembership
from records.models import Electricity, Maid, Record, Water

User = get_user_model()


class TestRecordModel(TransactionTestCase):
    """Test Record Model"""

    def setUp(self) -> None:
        self.adder = User.objects.create_user(
            email="test@user1.com",
            password="test-password",
            first_name="test",
            last_name="user1",
        )
        self.purchaser = User.objects.create_user(
            email="test@user2.com",
            password="test-password",
            first_name="test",
            last_name="user2",
        )
        self.room = Room.objects.create(name="test-room", admin=self.adder)

        # Create room membership for purchaser
        RoomMembership.objects.create(room=self.room, member=self.purchaser)

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
            room=self.room,
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
        self.assertEqual(
            str(record), f"{record.item} {record.purchaser} {self.room.name}"
        )

    def test_record_creation_for_invalid_purchaser(self) -> None:
        """Test record model instance creation for invalid purchaser"""

        # Create user
        user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )

        # Create record instance
        with self.assertRaisesMessage(
            ValidationError,
            "Purchaser is from the same room as the record.",
        ) as cm:
            Record.objects.create(
                item="test-item",
                price=99.99,
                purchaser=user,
                adder=self.adder,
                purchase_date=timezone.now().date(),
                room=self.room,
            )

        # Assert the expected error code
        self.assertEqual(cm.exception.code, "invalid_purchaser")

    def test_record_creation_for_invalid_adder(self) -> None:
        """Test record model instance creation for invalid adder"""

        # Create user
        user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )

        # Create record instance
        with self.assertRaisesMessage(
            ValidationError,
            "Adder is from the same room as the record.",
        ) as cm:
            Record.objects.create(
                item="test-item",
                price=99.99,
                purchaser=self.purchaser,
                adder=user,
                purchase_date=timezone.now().date(),
                room=self.room,
            )

        # Assert the expected error code
        self.assertEqual(cm.exception.code, "invalid_adder")

    def test_constraint_price_non_negative_and_less_than_100000(self) -> None:
        """Test constraint price non negative and less than 100000"""

        # Create record instance with negative price
        with self.assertRaisesMessage(
            IntegrityError,
            "CHECK constraint failed: price_non_negative_and_less_than_100000",
        ):
            Record.objects.create(
                item="test-item",
                price=-1,
                purchaser=self.purchaser,
                adder=self.adder,
                purchase_date=timezone.now().date(),
                room=self.room,
            )

        # Create record instance with price grater than 100000
        with self.assertRaisesMessage(
            IntegrityError,
            "CHECK constraint failed: price_non_negative_and_less_than_100000",
        ):
            Record.objects.create(
                item="test-item",
                price=2000000,
                purchaser=self.purchaser,
                adder=self.adder,
                purchase_date=timezone.now().date(),
                room=self.room,
            )

    def test_record_creation_for_feature_purchaser_date(self) -> None:
        """Test record model instance creation for feature purchaser date"""

        future_date = timezone.now().date() + timedelta(days=1)

        # Create record instance with price grater than 100000
        with self.assertRaisesMessage(
            IntegrityError,
            "CHECK constraint failed: purchase_date_within_last_six_days",
        ):
            Record.objects.create(
                item="item",
                price=10,
                purchaser=self.purchaser,
                adder=self.adder,
                purchase_date=future_date,
                room=self.room,
            )

    def test_record_creation_for_too_far_in_past_purchaser_date(self) -> None:
        """Test record model instance creation for too far in past purchaser date"""

        too_far_in_past_date = timezone.now().date() - timedelta(days=7)

        # Create record instance with price grater than 100000
        with self.assertRaisesMessage(
            IntegrityError,
            "CHECK constraint failed: purchase_date_within_last_six_days",
        ):
            Record.objects.create(
                item="item",
                price=10,
                purchaser=self.purchaser,
                adder=self.adder,
                purchase_date=too_far_in_past_date,
                room=self.room,
            )


class TestWaterModel(TestCase):
    """Test Water Model"""

    def setUp(self) -> None:
        self.adder = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )

        self.room = Room.objects.create(name="test-room", admin=self.adder)

    def test_water_creation(self) -> None:
        """Test water model instance creation"""

        # initialize data
        quantity = 1
        purchase_date = timezone.now().date()

        # create water instance
        water = Water.objects.create(
            quantity=quantity,
            adder=self.adder,
            room=self.room,
            purchase_date=purchase_date,
        )

        # assert field values
        self.assertEqual(water.quantity, quantity)
        self.assertEqual(water.adder, self.adder)
        self.assertEqual(water.purchase_date, purchase_date)
        # TODO: add assertion for modified_on field and created_on

        # assert string representation
        self.assertEqual(str(water), str(water.purchase_date))

    def test_record_creation_for_invalid_adder(self) -> None:
        """Test record model instance creation for invalid adder"""

        # Create user
        user = User.objects.create_user(
            email="test@user1.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )

        # Create record instance
        with self.assertRaisesMessage(
            ValidationError,
            "Adder is from the same room as the water.",
        ) as cm:
            Water.objects.create(
                quantity=1,
                adder=user,
                room=self.room,
                purchase_date=timezone.now().date(),
            )

        # Assert the expected error code
        self.assertEqual(cm.exception.code, "invalid_adder")


class TestElectricityModel(TestCase):
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


class TestMaidModel(TestCase):
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

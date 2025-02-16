from datetime import datetime, timedelta
from typing import Optional, Type

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import connection, models
from django.db.utils import IntegrityError
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from accounts.models import Room, RoomMembership
from records.models import BasePurchaseModel, Electricity, Maid, Record, Water

User = get_user_model()


class AbstractModelMixinTestCase(TransactionTestCase):
    """
    A test case that dynamically creates a model class based on the provided mixin
    and runs tests with that model
    """

    # mixin and model can initially be None, but will later be assigned a model class
    mixin: Optional[Type[models.Model]] = None
    model: Optional[Type[models.Model]] = None

    @classmethod
    def setUpClass(cls) -> None:
        # Ensure mixin is not None before attempting to create a model
        if cls.mixin is None:
            raise ValueError("Mixin class has not been set.")

        # Dynamically create a model by using the mixin as the base class
        cls.model = type(
            "TestModel" + cls.mixin.__name__,
            (cls.mixin,),  # Use the mixin as the base class
            {"__module__": cls.mixin.__module__},
        )

        # Create the model in the database schema
        with connection.schema_editor() as editor:
            editor.create_model(cls.model)

        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

        # Delete the dynamically created model from the schema, if model is not None
        if cls.model:
            with connection.schema_editor() as editor:
                editor.delete_model(cls.model)

        # Close the connection
        connection.close()


class TestBasePurchaseModel(AbstractModelMixinTestCase):
    """Test Base Purchase Model"""

    mixin = BasePurchaseModel

    def test_base_purchase_model_attributes(self) -> None:
        """Test base purchase model attributes"""

        self.assertEqual(BasePurchaseModel.max_allowed_past_days, 6)

    def test_base_purchase_model_creation_with_naive_purchase_datetime(self) -> None:
        """Test base purchase model instance creation with naive purchase datetime"""

        # create base purchase model instance with naive purchase datetime
        purchase = self.model.objects.create(purchase_datetime=datetime.now())

        # Assert that the datetime is now timezone-aware
        self.assertTrue(timezone.is_aware(purchase.purchase_datetime))

        # Assert if the timezone is the same as the current timezone
        self.assertEqual(
            purchase.purchase_datetime.tzinfo,
            timezone.get_current_timezone(),
        )

    def test_base_purchase_model_creation_for_feature_purchase_datetime(self) -> None:
        """Test base purchase model instance creation for feature purchase datetime"""

        future_datetime = timezone.now() + timedelta(days=1)

        # Create model instance with feature purchase datetime
        with self.assertRaisesMessage(
            ValidationError,
            "Purchase datetime should be within the past 6 days.",
        ) as cm:
            self.model.objects.create(purchase_datetime=future_datetime)

        # Assert the expected error code
        self.assertEqual(cm.exception.code, "invalid_purchase_datetime")

    def test_base_purchase_model_creation_for_too_far_in_past_purchase_datetime(
        self,
    ) -> None:
        """Test base purchase model  instance creation for too far in past purchase datetime"""

        too_far_in_past_datetime = timezone.now() - timedelta(days=7)

        # Create model instance with too far in past purchase datetime
        with self.assertRaisesMessage(
            ValidationError,
            "Purchase datetime should be within the past 6 days.",
        ) as cm:
            self.model.objects.create(purchase_datetime=too_far_in_past_datetime)

        # Assert the expected error code
        self.assertEqual(cm.exception.code, "invalid_purchase_datetime")


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
        purchase_datetime = timezone.now()

        # create record instance
        record = Record.objects.create(
            item=item,
            price=price,
            purchaser=self.purchaser,
            adder=self.adder,
            purchase_datetime=purchase_datetime,
            room=self.room,
        )

        # assert field values
        self.assertEqual(record.item, item)
        self.assertEqual(record.price, price)
        self.assertEqual(record.purchaser, self.purchaser)
        self.assertEqual(record.adder, self.adder)
        self.assertEqual(record.purchase_datetime, purchase_datetime)
        # TODO: add assertion for modified_on field and created_on
        # self.assertEqual(record.created_on, timezone.now())

        # assert string representation
        self.assertEqual(
            str(record),
            f"{record.item} {record.purchaser} {record.purchase_datetime} {self.room.name}",
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
                purchase_datetime=timezone.now(),
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
                purchase_datetime=timezone.now(),
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
                purchase_datetime=timezone.now(),
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
                purchase_datetime=timezone.now(),
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

    def test_water_model_attributes(self) -> None:
        """Test water model attributes"""

        self.assertEqual(Water.max_allowed_quality, 5)

    def test_water_creation(self) -> None:
        """Test water model instance creation"""

        # initialize data
        quantity = 1
        purchase_datetime = timezone.now()

        # create water instance
        water = Water.objects.create(
            quantity=quantity,
            adder=self.adder,
            room=self.room,
            purchase_datetime=purchase_datetime,
        )

        # assert field values
        self.assertEqual(water.quantity, quantity)
        self.assertEqual(water.adder, self.adder)
        self.assertEqual(water.purchase_datetime, purchase_datetime)
        # TODO: add assertion for modified_on field and created_on

        # assert string representation
        self.assertEqual(str(water), f"{water.purchase_datetime} {self.room.name}")

    def test_water_creation_for_invalid_adder(self) -> None:
        """Test water model instance creation for invalid adder"""

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
                purchase_datetime=timezone.now(),
            )

        # Assert the expected error code
        self.assertEqual(cm.exception.code, "invalid_adder")

    def test_water_creation_exceeds_max_quantity(self) -> None:
        """Test record model instance creation exceeds max quantity"""

        now = timezone.now()

        # Create record instance with quantity 6
        with self.assertRaisesMessage(
            ValidationError,
            "Maximum 5 water quantity allowed per day.",
        ) as cm1:
            Water.objects.create(
                quantity=6,
                adder=self.adder,
                room=self.room,
                purchase_datetime=now,
            )

        # Assert the expected error code
        self.assertEqual(cm1.exception.code, "exceeds_max_quantity")

        # Create record instance with quantity 5
        Water.objects.create(
            quantity=5,
            adder=self.adder,
            room=self.room,
            purchase_datetime=now,
        )

        # Create record instance with quantity 5
        with self.assertRaisesMessage(
            ValidationError,
            "Maximum 5 water quantity allowed per day.",
        ) as cm2:
            Water.objects.create(
                quantity=1,
                adder=self.adder,
                room=self.room,
                purchase_datetime=now,
            )

        # Assert the expected error code
        self.assertEqual(cm2.exception.code, "exceeds_max_quantity")


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

from datetime import date, datetime
from typing import Optional, Type

import pandas as pd

from accounts.models import User
from records.models import Electricity, Maid, Record, Water


class RoomExporter:
    """
    Helper class to get data related to a specific room (by room_id) for exporting.
    """

    def __init__(self, room_id: int):
        self.room_id = room_id

    def get_formatted_date(self, obj: date):
        """Returns formatted date for date object"""

        return obj.strftime("%d-%m-%Y")

    def get_formatted_time(self, obj: datetime):
        """Returns formatted time for time object"""

        return obj.strftime("%I:%M:%S %p")

    def get_entry_df(self, model: Type[Electricity | Maid]) -> pd.DataFrame:
        """
        Fetches entry for the given model filtered by room_id and returns a Pandas DataFrame.
        """

        # TODO: Filter the current room data once maid has room information
        entries = model.objects.all().order_by("due_date")

        data = [
            {
                "Date": self.get_formatted_date(entry.due_date),
                "Price": entry.price,
                "Entry ID": entry.id,
                "Entry Date": self.get_formatted_date(entry.created_on),
                "Entry Time": self.get_formatted_time(entry.created_on),
                "Last Modified Date": self.get_formatted_date(entry.modified_on),
                "Last Modified Time": self.get_formatted_time(entry.modified_on),
            }
            for entry in entries
        ]

        # Convert to Pandas DataFrame
        return pd.DataFrame(data)

    def get_water_df(self) -> pd.DataFrame:
        """
        Fetches entry for the water filtered by room_id and returns a Pandas DataFrame.
        """
        entries = Water.objects.filter(room_id=self.room_id).order_by("purchase_date")

        data = [
            {
                "Date": self.get_formatted_date(entry.purchase_date),
                "Quantity": entry.quantity,
                "Entry ID": entry.id,
                "Entry Date": self.get_formatted_date(entry.created_on),
                "Entry Time": self.get_formatted_time(entry.created_on),
                "Last Modified Date": self.get_formatted_date(entry.modified_on),
                "Last Modified Time": self.get_formatted_time(entry.modified_on),
                "Added By": entry.adder.get_full_name(),
            }
            for entry in entries
        ]

        # Convert to Pandas DataFrame
        return pd.DataFrame(data)

    def get_record_df(self, purchaser: Optional[User] = None) -> pd.DataFrame:
        """
        Fetches and returns a Pandas DataFrame of records for a given room.
        Optionally filters by a specific purchaser
        """

        queryset = Record.objects.filter(room_id=self.room_id)
        if purchaser:
            queryset = queryset.filter(purchaser=purchaser)
        records = queryset.order_by("purchase_datetime")

        # Prepare all records data
        data = [
            {
                "Purchase Date": self.get_formatted_date(record.purchase_datetime),
                "Purchase Time": self.get_formatted_time(record.purchase_datetime),
                "Item Name": record.item,
                "Price": record.price,
                "Purchase By": record.purchaser.get_full_name(),
                "Entry ID": record.id,
                "Entry Date": self.get_formatted_date(record.created_on),
                "Entry Time": self.get_formatted_time(record.created_on),
                "Last Modified Date": self.get_formatted_date(record.modified_on),
                "Last Modified Time": self.get_formatted_time(record.modified_on),
                "Added By": record.adder.get_full_name(),
            }
            for record in records
        ]

        # Convert to Pandas DataFrame
        return pd.DataFrame(data)

    def get_maid_df(self) -> pd.DataFrame:
        """Returns a DataFrame of maid records for a given room."""

        return self.get_entry_df(Maid)

    def get_electricity_df(self) -> pd.DataFrame:
        """Returns a DataFrame of electricity records for a given room."""

        return self.get_entry_df(Electricity)

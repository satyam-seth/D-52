from typing import Optional, Type

import pandas as pd

from accounts.models import User
from records.models import Electricity, Maid, Record


# pylint: disable=unused-argument
def get_entry_df(model: Type[Electricity | Maid], room_id: int) -> pd.DataFrame:
    """
    Fetches entry for the given model filtered by room_id and returns a Pandas DataFrame.
    """

    # TODO: Filter the current room data once maid has room information
    entries = model.objects.all().order_by("due_date")

    data = [
        {
            "Date": entry.due_date.strftime("%d-%m-%Y"),
            "Price": entry.price,
            "Entry ID": entry.id,
            "Entry Date": entry.created_on.strftime("%d-%m-%Y"),
            "Entry Time": entry.created_on.strftime("%H:%M:%S"),
            "Last Modified Date": entry.modified_on.strftime("%d-%m-%Y"),
            "Last Modified Time": entry.modified_on.strftime("%H:%M:%S"),
        }
        for entry in entries
    ]

    # Convert to Pandas DataFrame
    return pd.DataFrame(data)


def get_record_df(room_id: int, purchaser: Optional[User] = None) -> pd.DataFrame:
    """
    Fetches and returns a Pandas DataFrame of records for a given room.
    Optionally filters by a specific purchaser
    """

    queryset = Record.objects.filter(room_id=room_id)
    if purchaser:
        queryset = queryset.filter(purchaser=purchaser)
    records = queryset.order_by("purchase_date")

    # Prepare all records data
    data = [
        {
            "Purchase Date": record.purchase_date.strftime("%d-%m-%Y"),
            "Item Name": record.item,
            "Price": record.price,
            "Purchase By": record.purchaser.get_full_name(),
            "Entry ID": record.id,
            "Entry Date": record.created_on.strftime("%d-%m-%Y"),
            "Entry Time": record.created_on.strftime("%H:%M:%S"),
            "Last Modified Date": record.modified_on.strftime("%d-%m-%Y"),
            "Last Modified Time": record.modified_on.strftime("%H:%M:%S"),
            "Added By": record.adder.get_full_name(),
        }
        for record in records
    ]

    # Convert to Pandas DataFrame
    return pd.DataFrame(data)


def get_electricity_df(room_id: int) -> pd.DataFrame:
    """Returns a DataFrame of electricity records for a given room."""

    return get_entry_df(Electricity, room_id)


def get_maid_df(room_id: int) -> pd.DataFrame:
    """Returns a DataFrame of maid records for a given room."""

    return get_entry_df(Maid, room_id)

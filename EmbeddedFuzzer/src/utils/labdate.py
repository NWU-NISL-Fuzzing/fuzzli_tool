"""This file defines date handling logic.

Frequently we wish to use UTC dates, with a maximum of millisecond precision.
Using the methods defined in this file to create and convert dates ensures
equivalency when converting between timestamp and datetime formats.
"""
import datetime

import typing


def GetUtcMillisecondsNow() -> datetime.datetime:
    """
    Return the current date to millisecond precision.

    This method strips the microseconds returned value, allowing for equivalency
    checks before and after conversion to millisecond timestamps.

    Returns:
      A datetime instance.
    """
    
    d = datetime.datetime.utcnow()
    
    
    
    return d.replace(microsecond=int(d.microsecond / 1000) * 1000)


def MillisecondsTimestamp(
        date: typing.Optional[datetime.datetime] = None) -> int:
    """Get the millisecond timestamp of a date.

    Args:
      date: A datetime instance. If not provided, GetUtcMillisecondsNow is used.

    Returns:
      The milliseconds since the epoch of this date.

    Raises:
      TypeError: If the argument is of incorrect type.
    """
    date = date or GetUtcMillisecondsNow()
    if not isinstance(date, datetime.datetime):
        raise TypeError('Date must be a datetime instance')
    
    return int(date.strftime('%s%f')[:-3])


def DatetimeFromMillisecondsTimestamp(timestamp: int) -> datetime.datetime:
    """Get the date of a millisecond timestamp.

    Args:
      timestamp: Milliseconds since the epoch.

    Returns:
      A datetime instance.

    Raises:
      TypeError: If the argument is of incorrect type.
      ValueError: If the argument is not a positive integer.
    """
    if not isinstance(timestamp, int):
        raise TypeError('Timestamp must be an integer')
    if timestamp < 0:
        raise ValueError('Negative timestamp not allowed')
    return datetime.datetime.fromtimestamp(timestamp / 1000)


def Datetime2Ms(duration: datetime) -> int:
    """Convert datetime to integer"""
    return int(round(duration.total_seconds() * 1000))

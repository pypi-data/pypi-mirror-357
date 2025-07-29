from datetime import datetime, timedelta
import re

RELATIVE_TIME_PATTERN = re.compile(r'([-+])?(\d{3}\.)?(\d{2}):(\d{2}):(\d{2})(\.\d{3})?')
MS_SEC = 1000;
SEC_MINUTE = 60;
MINUTE_HOUR = 60;
HOUR_DAY = 24;
MS_DAY = HOUR_DAY * MINUTE_HOUR * SEC_MINUTE * MS_SEC;
MS_HOUR = MINUTE_HOUR * SEC_MINUTE * MS_SEC;
MS_MINUTE = SEC_MINUTE * MS_SEC

def parse_relative_time(relative: str) -> int:
    """
    Parses a relative time string and converts it to milliseconds.

    The relative time string should be in the format [+|-][DDD.]HH:MM:SS[.mmm], where:
    - DDD is the number of days (optional)
    - HH is the number of hours
    - MM is the number of minutes
    - SS is the number of seconds
    - mmm is the number of milliseconds (optional)
    - The sign (+ or -) indicates whether the time is positive or negative (optional)

    Args:
        relative (str): The relative time string to parse.

    Returns:
        int: The total time in milliseconds. 
        
    If the input string is invalid, raises an EventResolverException.
    """
    matcher = RELATIVE_TIME_PATTERN.match(relative)
    if matcher:
        groups = matcher.groups()
        sign =  -1 if groups[0] == '-' else 1
        day = groups[1]
        hour = int(groups[2])
        minute = int(groups[3])
        second = int(groups[4])
        ms = groups[5]
        day = int(day[0:3]) if day else 0
        ms = int(ms[1:4]) if ms else 0
        return sign * (day * MS_DAY + hour * MS_HOUR + minute * MS_MINUTE + second * MS_SEC + ms)
    else:
        raise Exception('Relative time not valid')


def parse_time(utc: str) -> datetime:
    """
    Args:
        utc (str): "2023-104T12:47:12.000Z" or  "2023-10-04T12:47:12.000Z"

    Returns:
        datetime: the corresponding date
    """
    try:
        date = parse_fdyn_time(utc)
    except ValueError:
        date = parse_utc_time(utc)
        return date
    else:
        return date


def parse_fdyn_time(doy_utc: str) -> datetime:
    """
    Args:
        doy_utc (str): "2023-104T12:47:12.000Z"

    Returns:
        datetime: the corresponding date
    """
    fdyn_format = "%Y-%jT%H:%M:%S.%fZ"
    return datetime.strptime(doy_utc, fdyn_format)


def parse_utc_time(utc_time: str) -> datetime:
    """
    Args:
        utc (str): "2023-10-04T12:47:12.000Z"

    Returns:
        datetime: the corresponding date
    """
    utc_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    return datetime.strptime(utc_time, utc_format)


def format_iso(date: datetime) -> str:
    """
    Args:
        date (datetime)

    Returns:
        str: the ISOC representation "2023-10-04T12:47:12.000Z"
    """

    return datetime.strftime(date, "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def format_doy(date: datetime) -> str:
    """
    Args:
        date (datetime)

    Returns:
        str: the ISOC representation "2023-104T12:47:12.000Z"
    """

    return datetime.strftime(date, "%Y-%jT%H:%M:%S.%f")[:-3] + "Z"


def fdyn_to_iso(doy_utc: str) -> str:
    """
    Args:
        doy_utc (str): "2023-104T12:47:12.000Z"

    Returns:
        str: the ISOC representation "2023-104T12:47:12Z"
    """
    return format_iso(parse_time(doy_utc))


def iso_to_fdyn(iso_utc: str) -> str:
    """
    Args:
        iso_utc (str): "2023-10-04T12:47:12.000Z"

    Returns:
        str: the FDYB representation "2023-104T12:47:12.000Z"
    """
    return format_doy(parse_time(iso_utc))


def get_timedelta(milliseconds: str) -> timedelta:
    """The time delta object corresponding to the milliseconds string

    Args:
        milliseconds (str): duration expressed in milliseconds

    Returns:
        timedelta: the corresponding time delta
    """
    return timedelta(milliseconds=int(milliseconds))
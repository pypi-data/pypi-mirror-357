from datetime import datetime, timedelta
from phs.timeline.event_parser import EvtcParser
from phs.timeline.time_utils import parse_relative_time
import requests
from pathlib import Path

def get_uvt_events(uevt, server='https://juicesoc.esac.esa.int'):
    """
    Fetches UVT event details from the specified server.

    Args:
        uevt (str): The unique identifier for the UVT event.
        server (str): The server URL to fetch the UVT event from. Defaults to 'https://juicesoc.esac.esa.int'.

    Returns:
        list: list containing the UVT events .
    """
    response = requests.get(f'{server}/rest_api/uvt_event/{uevt}')
    if response.status_code != 200:
            raise EventResolverException(f'Events for {uevt} not available')
    return response.json()

def get_uvt_list(server='https://juicesoc.esac.esa.int'):
    """
    Fetches a list of all UVT events from the specified server.

    Args:
        server (str): The server URL to fetch the UVT events from. Defaults to 'https://juicesoc.esac.esa.int'.

    Returns:
        dict: A dictionary containing the list of UVT events.
    """
    response = requests.get(f'{server}/rest_api/uvt_event_file')
    if response.status_code != 200:
            raise EventResolverException('UVT list not available')
    return response.json()


def parse_utc(utc: str) -> datetime:
    return datetime.fromisoformat(utc[:-1])

def format_utc(dt: datetime) -> str:
    return dt.isoformat(timespec='milliseconds') + 'Z'


class EventResolverException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class EventResolver:

    @staticmethod
    def from_rest_api(uvt: str):
        uvt_files = [item.get('mnemonic') for item in get_uvt_list()]
        if uvt not in uvt_files:
            raise EventResolverException(f'{uvt} not available')
        return EventResolver(get_uvt_events(uvt))

    @staticmethod
    def from_file(uvt_file: Path):
        parser = EvtcParser(uvt_file)
        return EventResolver(parser.events)

    def __init__(self, events: any) -> None:
        self.events = events

    def search_event(self, mnemonic: str, counter: int) -> any:
        events = list(filter(
                    lambda event: event.get('mnemonic') == mnemonic and event.get('count') == counter,
                    self.events))
        if len(events) == 0:
            raise EventResolverException(f'Event {mnemonic} (#{counter}) not available')
        return events[0]

    def resolve(self, event_mnemonic: str, counter: int, relative: str, duration: str) -> (str, str):
        duration_ms = parse_relative_time(duration)
        relative_ms = parse_relative_time(relative)

        event = self.search_event(event_mnemonic, counter)

        event_time = parse_utc(event.get('time'))
        start = event_time + timedelta(milliseconds=relative_ms)
        end = start + timedelta(milliseconds=duration_ms)

        return (format_utc(start), format_utc(end))

    def resolve_apl(self, apl_json):
        # Extract the activities
        activities = apl_json['activities']

        # Iterate through activities
        for activity in activities:
            event = activity.get('event')
            counter = activity.get('counter')
            relative = activity.get('relative')
            duration = activity.get('duration')
            start, end = self.resolve(event, counter, relative, duration)
            activity['start'] = start
            activity['end'] = end
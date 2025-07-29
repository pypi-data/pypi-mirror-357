from xml.etree import ElementTree
from typing import Any

from phs.timeline.time_utils import fdyn_to_iso

class AbstractParser:

    def __init__(self, path: Any) -> None:
        self.path = path
        self.doc = ElementTree.parse(path)
        self.root = self.doc.getroot()


class EvtcParser(AbstractParser):

    def __init__(self, path: Any) -> None:
        AbstractParser.__init__(self, path)
        self.ns_map = {"ns": "http://esa.esoc.events", "ems": "http://esa.esoc.ems"}
        self.__xml_events = self.root.findall(".//ns:events/*", self.ns_map)
        self.__to_json()

    def __entry_to_json(self, entry):
        return {
            'mnemonic': entry.get('id'),
            'count': int(entry.get('count')),
            'time': fdyn_to_iso(entry.get('time')),
        }

    def __to_json(self):
        self.events = [ self.__entry_to_json(entry) for entry in self.__xml_events]
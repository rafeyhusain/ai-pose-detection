from typing import List
from sdk.detection.report.report_item import ReportItem

class Report:
    def __init__(self):
        self._items: List[ReportItem] = []

    @property
    def items(self) -> List[ReportItem]:
        return self._items

    @items.setter 
    def items(self, value: List[ReportItem]):
        self._items = value



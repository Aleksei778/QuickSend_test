from pydantic import BaseModel

from typing import List, OrderedDict


class SheetRequest(BaseModel):
    spreadsheet_id: str
    range: str


class EmailList(BaseModel):
    emails: List[str]
    spreadsheet_name: str

    def remove_dups(self):
        self.emails = list(OrderedDict.fromkeys(self.emails))

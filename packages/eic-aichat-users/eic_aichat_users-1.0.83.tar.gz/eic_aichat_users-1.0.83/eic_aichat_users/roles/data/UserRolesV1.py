# -*- coding: utf-8 -*-
from typing import List, Optional
from datetime import datetime

from pip_services4_data.data import IStringIdentifiable


class UserRolesV1(IStringIdentifiable):
    def __init__(
        self,
        id: Optional[str] = None,
        roles: Optional[List[str]] = None
    ):
        self.id: str = id
        self.roles: List[str] = roles or []
        self.update_time: datetime = datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "roles": self.roles,
            "update_time": self.update_time.isoformat() if isinstance(self.update_time, datetime) else self.update_time
        }
    
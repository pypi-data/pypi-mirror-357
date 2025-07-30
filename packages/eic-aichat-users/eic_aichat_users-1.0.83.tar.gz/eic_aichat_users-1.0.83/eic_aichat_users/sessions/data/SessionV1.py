# session_v1.py
from typing import Any, Optional
from datetime import datetime
from pip_services4_data.data import IStringIdentifiable
from pip_services4_data.keys import IdGenerator

class SessionV1(IStringIdentifiable):
    def __init__(
        self,
        id: Optional[str] = None,
        user_id: str = '',
        user_name: Optional[str] = '',
        address: Optional[str] = '',
        client: Optional[str] = ''
    ):
        self.id: str = id or IdGenerator.next_long()
        self.user_id: str = user_id
        self.user_name: Optional[str] = user_name
        self.active: bool = True
        self.open_time: datetime = datetime.utcnow()
        self.request_time: datetime = datetime.utcnow()
        self.close_time: Optional[datetime] = None
        self.address: Optional[str] = address
        self.client: Optional[str] = client
        self.user: Optional[Any] = None
        self.data: Optional[Any] = None

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "active": self.active,
            "open_time": self.open_time.isoformat() if isinstance(self.open_time, datetime) else self.open_time,
            "request_time": self.request_time.isoformat() if isinstance(self.request_time, datetime) else self.request_time,
            "close_time": self.close_time.isoformat() if isinstance(self.close_time, datetime) else self.close_time,
            "address": self.address,
            "client": self.client,
            "user": self.user.to_dict() if hasattr(self.user, 'to_dict') else self.user,
            "data": self.data 
        }

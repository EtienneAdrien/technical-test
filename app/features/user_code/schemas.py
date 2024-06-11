from datetime import datetime

from pydantic import BaseModel


class UserCode(BaseModel):
    user_id: int
    code: str
    date_start_validity: datetime | None

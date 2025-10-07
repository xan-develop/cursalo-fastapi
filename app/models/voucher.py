from beanie import Document, Link
from datetime import datetime
from typing import Optional
from pydantic import Field
class Voucher(Document):
    student: Link["Student"] # type: ignore
    total_credits: int
    remaining_credits: int
    price: float
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    class Settings:
        name = "vouchers"

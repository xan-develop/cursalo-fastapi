from beanie import Document, Link
from datetime import datetime
from typing import Optional , TYPE_CHECKING
from pydantic import Field

if TYPE_CHECKING:
    from models.users import Student
class Voucher(Document):
    student: Link["Student"]  
    total_credits: int
    remaining_credits: int
    price: float
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    class Settings:
        name = "vouchers"

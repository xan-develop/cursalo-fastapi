from beanie import Document, Link
from datetime import datetime
from typing import Optional , TYPE_CHECKING
from pydantic import Field

if TYPE_CHECKING:
    from models.users import Student
    from models.classes import Class

class VoucherHistory(Document):
    student: Link["Student"]
    class_item: Link["Class"]
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "voucher_history"

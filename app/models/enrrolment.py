from beanie import Document, Link
from datetime import datetime
from typing import Literal, Optional
from pydantic import Field


class Enrollment(Document):
    student: Link["Student"] # type: ignore
    class_: Link["Class"] # type: ignore
    payment_type: Literal["direct", "voucher"]
    voucher_used: Optional[Link["Voucher"]] = None # type: ignore
    enrolled_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "enrollments"

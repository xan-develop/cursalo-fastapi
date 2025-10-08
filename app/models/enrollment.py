from beanie import Document, Link
from datetime import datetime
from typing import Literal, Optional , TYPE_CHECKING
from pydantic import BaseModel, Field



if TYPE_CHECKING:
    from models.users import Student
    from models.classes import Class
    from models.voucher import Voucher
class Enrollment(Document):
    student: Link["Student"]
    class_: Link["Class"]
    payment_type: Literal["direct", "voucher"]
    voucher_used: Optional[Link["Voucher"]] = None
    enrolled_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "enrollments"

class EnrollmentRequest(BaseModel):
    student_id: str
    payment_type: Literal["direct", "voucher"]
    voucher_id: Optional[str] = None
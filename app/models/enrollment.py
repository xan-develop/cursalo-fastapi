from beanie import Document, Link
from datetime import datetime
from typing import Literal, Optional , TYPE_CHECKING
from pydantic import BaseModel, Field



if TYPE_CHECKING:
    from models.users import Student
    from models.classes import Class

class Enrollment(Document):
    student: Link["Student"]
    class_: Link["Class"]
    payment_type: Literal["direct", "voucher"]
    enrolled_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "enrollments"

class EnrollmentRequest(BaseModel):
    student_id: str
    class_id: str
    payment_type: Literal["direct", "voucher"]
    
class EnrollmentResponse(BaseModel):
    id: str
    student_id: str
    class_id: str
    student_name: str
    class_title: str
    payment_type: Literal["direct", "voucher"]
    enrolled_at: datetime
    
    @classmethod
    def from_enrollment(cls, enrollment: Enrollment) -> "EnrollmentResponse":
        return cls(
            id=str(enrollment.id),
            student_id=str(enrollment.student.id), # type: ignore Documentacion de beanie sobre referencias
            class_id=str(enrollment.class_.id), # type: ignore Documentacion de beanie sobre referencias
            student_name=enrollment.student.full_name or enrollment.student.username, # type: ignore Documentacion de beanie sobre referencias
            class_title=enrollment.class_.title, # type: ignore Documentacion de beanie sobre referencias
            payment_type=enrollment.payment_type,
            enrolled_at=enrollment.enrolled_at
        )

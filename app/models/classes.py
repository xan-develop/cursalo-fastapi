from beanie import Document, Link 
from typing import List, Optional , TYPE_CHECKING
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from decimal import Decimal
from bson import Decimal128

if TYPE_CHECKING:
    from models.users import Teacher, Student

class Class(Document):
    title: str
    description: Optional[str] = None
    teacher: Link["Teacher"]
    price: Decimal
    allow_voucher: bool = True
    max_students: Optional[int] = None
    start_date: datetime
    duration_minutes: int
    created_at: datetime = Field(default_factory=datetime.now)
    enrolled_students: List[Link["Student"]] = Field(default_factory=list)

    # Validador para convertir Decimal128 a Decimal
    @field_validator('price', mode='before')
    @classmethod
    def convert_decimal128_to_decimal(cls, v):
        if isinstance(v, Decimal128):
            return Decimal(str(v))
        return v

    class Settings:
        name = "classes"

class ClassCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    teacher_id: str
    price: Decimal
    allow_voucher: bool = True
    max_students: Optional[int] = None
    start_date: datetime
    duration_minutes: int

    # Validador para el request
    @field_validator('price', mode='before')
    @classmethod
    def convert_decimal128_to_decimal(cls, v):
        if isinstance(v, Decimal128):
            return Decimal(str(v))
        return v

class ClassUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    allow_voucher: Optional[bool] = None
    max_students: Optional[int] = None
    start_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    
    # Validador para el update 
    @field_validator('price', mode='before')
    @classmethod
    def convert_decimal128_to_decimal(cls, v):
        if v is not None and isinstance(v, Decimal128):
            return Decimal(str(v))
        return v

class ClassResponse(ClassCreateRequest):
    id: str
    teacher_name: str
    enrolled_students_count: int = 0

    @classmethod
    def from_model(cls, class_model: Class) -> "ClassResponse":
        return cls(
            id=str(class_model.id),
            title=class_model.title,
            description=class_model.description,
            teacher_id=str(class_model.teacher.id),  # type: ignore
            teacher_name=class_model.teacher.username, # type: ignore
            enrolled_students_count=len(class_model.enrolled_students),
            price=class_model.price,
            allow_voucher=class_model.allow_voucher,
            max_students=class_model.max_students,
            start_date=class_model.start_date,
            duration_minutes=class_model.duration_minutes,
        )
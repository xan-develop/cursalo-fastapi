from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import datetime
from decimal import Decimal
from bson import Decimal128
import pymongo
from beanie import Document, Link

# Import condicional para evitar referencias circulares
if TYPE_CHECKING:
    from models.classes import Class
    from models.voucher import Voucher

class User(Document):
    username: str
    email: str
    full_name: Optional[str] = None
    password: str
    role: str
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

    class Settings:
        name = "users"
        is_root = True
        indexes = [
            [("username", pymongo.ASCENDING)],
            [("email", pymongo.ASCENDING)],
            [("role", pymongo.ASCENDING)],
        ]
        
class Teacher(User):
    role: str = "teacher"  # fijo
    biography: Optional[str] = None
    specialization: Optional[str] = None
    created_classes: List[Link["Class"]] = Field(default_factory=list)  # ✅ Cambiar Optional y usar Field
    
    # Validador para manejar Decimal128 en objetos anidados
    @model_validator(mode='before')
    @classmethod
    def convert_decimal128_fields(cls, values):
        def convert_decimal128_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, Decimal128):
                        obj[key] = Decimal(str(value))
                    elif isinstance(value, (dict, list)):
                        convert_decimal128_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    convert_decimal128_recursive(item)
        
        if isinstance(values, dict):
            convert_decimal128_recursive(values)
        return values
    
class Student(User):
    role: str = "student"  # fijo
    vouchers: List[Link["Voucher"]] = Field(default_factory=list)  # ✅ Cambiar Optional y usar Field
    enrolled_classes: List[Link["Class"]] = Field(default_factory=list)  # ✅ Cambiar Optional y usar Field

    # Mismo validador para Student
    @model_validator(mode='before')
    @classmethod
    def convert_decimal128_fields(cls, values):
        def convert_decimal128_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, Decimal128):
                        obj[key] = Decimal(str(value))
                    elif isinstance(value, (dict, list)):
                        convert_decimal128_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    convert_decimal128_recursive(item)
        
        if isinstance(values, dict):
            convert_decimal128_recursive(values)
        return values

class TeacherRegistration(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    password: str
    biography: Optional[str] = None
    specialization: Optional[str] = None

class StudentRegistration(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    password: str

# Response model SIN referencias circulares
class TeacherResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    biography: Optional[str] = None
    specialization: Optional[str] = None
    created_classes_count: int = 0  # Solo el count, no los objetos completos
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_teacher(cls, teacher: Teacher) -> "TeacherResponse":
        """Convierte un Teacher a TeacherResponse"""
        return cls(
            id=str(teacher.id),
            username=teacher.username,
            email=teacher.email,
            full_name=teacher.full_name,
            role=teacher.role,
            biography=teacher.biography,
            specialization=teacher.specialization,
            created_classes_count=len(teacher.created_classes) if teacher.created_classes else 0,
            created_at=teacher.created_at,
            is_active=teacher.is_active
        )

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

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str
    
class User(Document):
    username: str
    email: str
    full_name: Optional[str] = None
    password: str
    phone: Optional[str] = None
    address: Optional[Address] = None
    role: str
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

    @model_validator(mode='before')
    @classmethod
    def handle_none_values_and_decimal128(cls, values):
        # AGREGAR: Debug temporal
        if isinstance(values, dict) and values.get('role') == 'student':
            print(f"DEBUG Student data: {values}")
        
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
        
            convert_decimal128_recursive(values)
        return values

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
    created_classes: List[Link["Class"]] = Field(default_factory=list) 
    
class Student(User):
    role: str = "student"  # fijo
    vouchers: List[Link["Voucher"]] = Field(default_factory=list) 
    enrolled_classes: List[Link["Class"]] = Field(default_factory=list) 

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
    phone: Optional[str] = None
    address: Optional[Address] = None
    password: str

# Response models para evitar exponer campos sensibles y referencias circulares
class TeacherResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    biography: Optional[str] = None
    specialization: Optional[str] = None
    created_classes_count: int = 0  
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
        
class StudentResponse(BaseModel):
    id: str
    username: str
    email: str
    phone: Optional[str] = None
    address: Optional[Address] = None
    full_name: Optional[str] = None
    role: str
    enrolled_classes_count: int = 0  
    vouchers_count: int = 0
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_student(cls, student: Student) -> "StudentResponse":
        """Convierte un Student a StudentResponse"""
        return cls(
            id=str(student.id),
            username=student.username,
            email=student.email,
            full_name=student.full_name,
            role=student.role,
            enrolled_classes_count=len(student.enrolled_classes) if student.enrolled_classes else 0,
            vouchers_count=len(student.vouchers) if student.vouchers else 0,
            created_at=student.created_at,
            is_active=student.is_active,
            phone=student.phone,
            address=student.address
        )
        
class StudentUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    address: Optional[Address] = None
    phone: Optional[str] = None

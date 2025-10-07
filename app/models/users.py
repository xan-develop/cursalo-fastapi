from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import pymongo
from beanie import Document, Link

class User(Document):
    username: str
    email: str
    full_name: Optional[str] = None
    password: str
    role: str  # Ejemplo: "admin", "user", "teacher"
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

    class Settings:
        name = "users"  # Nombre de la colección en MongoDB
        is_root = True
        indexes = [
            [("username", pymongo.ASCENDING)],  # Índice para búsquedas rápidas por nombre de usuario
            [("email", pymongo.ASCENDING)]      # Índice para búsquedas rápidas por correo electrónico
        ]
        
class Teacher(User):
    role: str = "teacher"  # fijo
    biography: Optional[str] = None
    specialization: Optional[str] = None
    created_classes: Optional[List[Link["Class"]]] = []   # type: ignore # Forward reference como string
    
        
class Student(User):
    role: str = "student"  # fijo
    vouchers: Optional[List[Link["Voucher"]]] = []  # type: ignore # Forward reference como string
    enrolled_classes: Optional[List[Link["Class"]]] = []  # type: ignore # Forward reference como string

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
    vouchers: List[str] = []
    enrolled_classes: List[str] = []
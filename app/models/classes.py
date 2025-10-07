from beanie import Document, Link 
from typing import List, Optional 
from pydantic import Field
from datetime import datetime
from decimal import Decimal

class Class(Document):
    title: str
    description: Optional[str]
    teacher: Link["Teacher"] # type: ignore
    price: Decimal
    allow_voucher: bool = True  # si se puede usar bono
    max_students: Optional[int] = None
    start_date: datetime
    duration_minutes: int
    created_at: datetime = Field(default_factory=datetime.now)
    enrolled_students: List[Link["Student"]] = [] # type: ignore

    class Settings:
        name = "classes"

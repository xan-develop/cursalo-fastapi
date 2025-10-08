from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional, Tuple
from models.classes import Class, ClassCreateRequest
from models.users import Teacher, Student

class ClassValidator:
    
    @staticmethod
    def _get_current_time() -> datetime:
        """Obtiene la hora actual con timezone UTC"""
        return datetime.now(timezone.utc)

    @staticmethod
    def _ensure_timezone_aware(dt: datetime) -> datetime:
        """Asegura que un datetime tenga información de timezone"""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @staticmethod
    def validate_class_start_date(start_date: datetime) -> datetime:
        """Valida la fecha de inicio de la clase"""
        start_date_aware = ClassValidator._ensure_timezone_aware(start_date)
        current_time = ClassValidator._get_current_time()
        
        if start_date_aware <= current_time:
            raise ValueError("The class start date must be in the future")
        
        # Verificar que la fecha no sea mayor a 2 meses en el futuro
        max_date = current_time + timedelta(days=60)
        if start_date_aware > max_date:
            raise ValueError("The class start date cannot be more than 2 months in the future")
        
        return start_date_aware

    @staticmethod
    def validate_duration(duration_minutes: int) -> None:
        """Valida la duración de la clase"""
        if duration_minutes <= 0:
            raise ValueError("The class duration must be greater than zero")
        if duration_minutes > 480:
            raise ValueError("The class duration cannot exceed 480 minutes (8 hours)")

    @staticmethod
    def validate_price(price: Decimal) -> None:
        """Valida el precio de la clase"""
        if price < 0:
            raise ValueError("The class price cannot be negative")
        if price > Decimal('999'):
            raise ValueError("The class price cannot exceed 999")

    @staticmethod
    def validate_max_students(max_students: Optional[int]) -> None:
        """Valida el máximo de estudiantes"""
        if max_students is not None and max_students <= 0:
            raise ValueError("The maximum number of students must be greater than zero")
        if max_students is not None and max_students > 100:
            raise ValueError("The maximum number of students cannot exceed 100")

    @staticmethod
    def validate_teacher_availability(existing_classes: List[Class], teacher: Teacher) -> None:
        """Valida que el profesor no tenga clases en el mismo horario"""
        for existing_class in existing_classes:
            if existing_class.teacher.id == teacher.id:
                raise ValueError("The teacher already has a class scheduled at this time")

    @staticmethod
    def validate_class_not_enrolled(class_item: Class) -> None:
        """Valida que la clase no tenga estudiantes inscritos para poder eliminarla"""
        if len(class_item.enrolled_students) > 0:
            raise ValueError("No se puede eliminar una clase con estudiantes inscritos")

    @staticmethod
    def validate_search_term(title: str) -> str:
        """Valida el término de búsqueda"""
        if not title or len(title.strip()) < 2:
            raise ValueError("El término de búsqueda debe tener al menos 2 caracteres")
        return title.strip()

    @staticmethod
    def validate_price_range(min_price: Decimal, max_price: Decimal) -> None:
        """Valida el rango de precios"""
        if min_price < 0 or max_price < 0:
            raise ValueError("Los precios no pueden ser negativos")
        
        if min_price > max_price:
            raise ValueError("El precio mínimo no puede ser mayor al máximo")

    @staticmethod
    def _has_available_spots(class_item: Class) -> bool:
        """Verifica si una clase tiene cupos disponibles"""
        if class_item.max_students is None:
            return True
        return len(class_item.enrolled_students) < class_item.max_students

    @staticmethod
    def has_available_spots(class_item: Class) -> bool:
        """Verifica si una clase tiene cupos disponibles """
        return ClassValidator._has_available_spots(class_item)

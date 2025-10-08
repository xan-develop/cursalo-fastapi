from pydantic import ValidationError
from repositories.class_repo import ClassRepo
from repositories.auth_repo import AuthRepo
from models.classes import Class, ClassCreateRequest, ClassUpdateRequest
from models.users import Teacher, Student
from validators.class_validator import ClassValidator
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from beanie import Link, WriteRules
from repositories.class_repo import get_class_repo
from repositories.auth_repo import get_auth_repo

class ClassService:
    def __init__(self, class_repo: ClassRepo, auth_repo: AuthRepo):
        self.class_repo = class_repo
        self.auth_repo = auth_repo

    def _get_current_time(self) -> datetime:
        """Obtiene la hora actual con timezone UTC"""
        return datetime.now(timezone.utc)

    def _ensure_timezone_aware(self, dt: datetime) -> datetime:
        """Asegura que un datetime tenga información de timezone"""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    async def create_class(self, class_data: ClassCreateRequest) -> Class:
        """Crea una nueva clase con validaciones de negocio"""
        # Verificar que el profesor existe
        teacher = await self.auth_repo.get_teacher_by_id(class_data.teacher_id)
        if not teacher:
            raise ValueError("This teacher does not exist")
        if class_data.teacher_id != str(teacher.id):
            raise ValueError("Cant create class for a non-existing teacher")
        # Validar fecha de inicio
        start_date_aware = ClassValidator.validate_class_start_date(class_data.start_date)
        
        ClassValidator.validate_duration(class_data.duration_minutes)
        ClassValidator.validate_price(class_data.price)
        ClassValidator.validate_max_students(class_data.max_students)
        
        # Calcular end_date con timezone
        end_date_aware = start_date_aware + timedelta(minutes=class_data.duration_minutes)
        
        # Verificar disponibilidad del profesor
        existing_classes = await self.class_repo.find_by_date_range(
            start_date_aware, 
            end_date_aware
        )
        ClassValidator.validate_teacher_availability(existing_classes, teacher)

        # Crear la clase con la fecha corregida
        class_data_dict = class_data.model_dump(exclude={"teacher_id"})
        class_data_dict['start_date'] = start_date_aware
        
        new_class = Class(
            **class_data_dict,
            teacher=teacher  # type: ignore
        )
        class_response = await self.class_repo.create(new_class)
        teacher.created_classes.append(class_response) # type: ignore 
        await teacher.save()
        return class_response

    async def get_class_by_id(self, class_id: str) -> Class | None:
        """Obtiene una clase por ID"""
        return await self.class_repo.get_by_id(class_id)

    async def get_all_classes(self) -> List[Class]:
        """Obtiene todas las clases"""
        return await self.class_repo.get_all()

    async def update_class(self, class_id: str, update_data: ClassUpdateRequest) -> Class | None:
        """Actualiza una clase existente"""
        class_item = await self.class_repo.get_by_id(class_id)
        if not class_item:
            return None

        # Aplicar solo los campos que no son None
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(class_item, key, value)

        return await self.class_repo.update(class_item)

    async def delete_class(self, class_id: str) -> bool:
        """Elimina una clase"""
        class_item = await self.class_repo.get_by_id(class_id)
        if not class_item:
            return False
        
        # Validar que no tenga estudiantes inscritos
        ClassValidator.validate_class_not_enrolled(class_item)

        await self.class_repo.delete(class_item)
        return True

    async def get_classes_by_teacher(self, teacher_id: str) -> List[Class]:
        """Obtiene todas las clases de un profesor"""
        teacher = await self.auth_repo.get_teacher_by_id(teacher_id)
        if not teacher:
            return []
        
        return await self.class_repo.find_by_teacher(teacher)

    async def get_available_classes(self) -> List[Class]:
        """Obtiene clases disponibles (futuras y con cupos)"""
        current_time = self._get_current_time()
        future_classes = await self.class_repo.find_future_classes(current_time)
        
        # Filtrar solo las que tienen cupos disponibles
        available_classes = []
        for class_item in future_classes:
            if ClassValidator.has_available_spots(class_item):
                available_classes.append(class_item)
        
        return available_classes

    async def get_upcoming_classes(self, days_ahead: int = 7) -> List[Class]:
        """Obtiene clases que empiezan en los próximos días"""
        current_time = self._get_current_time()
        future_time = current_time.replace(hour=23, minute=59, second=59) + timedelta(days=days_ahead)
        
        return await self.class_repo.find_by_date_range(current_time, future_time)

    async def search_classes_by_title(self, title: str) -> List[Class]:
        """Busca clases por título"""
        validated_title = ClassValidator.validate_search_term(title)
        return await self.class_repo.find_by_title_pattern(validated_title)

    async def get_classes_by_price_range(self, min_price: Decimal, max_price: Decimal) -> List[Class]:
        """Obtiene clases dentro de un rango de precios"""
        ClassValidator.validate_price_range(min_price, max_price)
        return await self.class_repo.find_by_price_range(float(min_price), float(max_price))

    async def get_class_enrollment_count(self, class_id: str) -> int:
        """Obtiene el número de estudiantes inscritos en una clase"""
        class_item = await self.class_repo.get_by_id(class_id)
        if not class_item:
            return 0
        return len(class_item.enrolled_students)

    async def is_class_full(self, class_id: str) -> bool:
        """Verifica si una clase está llena"""
        class_item = await self.class_repo.get_by_id(class_id)
        if not class_item:
            return True
        
        return not ClassValidator.has_available_spots(class_item)

    async def can_enroll_student(self, class_id: str, student_id: str) -> tuple[bool, str]:
        """Verifica si un estudiante puede inscribirse a una clase"""
        class_item = await self.class_repo.get_by_id(class_id)
        student = await self.auth_repo.get_student_by_id(student_id)
        
        return ClassValidator.validate_class_enrollment(class_item, student)

    def _has_available_spots(self, class_item: Class) -> bool:
        """Verifica si una clase tiene cupos disponibles"""
        if class_item.max_students is None:
            return True
        return len(class_item.enrolled_students) < class_item.max_students

# Función para dependency injection
def get_class_service() -> ClassService:
    class_repo = get_class_repo()
    auth_repo = get_auth_repo()
    return ClassService(class_repo, auth_repo)
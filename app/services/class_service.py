from pydantic import ValidationError
from repositories.class_repo import ClassRepo
from repositories.auth_repo import AuthRepo
from models.classes import Class, ClassCreateRequest, ClassUpdateRequest
from models.users import Teacher, Student
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from beanie import Link, WriteRules
from repositories.class_repo import get_class_repo
from repositories.auth_repo import get_auth_repo

class ClassService:
    def __init__(self, class_repo: ClassRepo, auth_repo: AuthRepo):
        self.class_repo = class_repo
        self.auth_repo = auth_repo

    async def create_class(self, class_data: ClassCreateRequest) -> Class:
        """Crea una nueva clase con validaciones de negocio"""
        # Verificar que el profesor existe
        teacher = await self.auth_repo.get_teacher_by_id(class_data.teacher_id)
        if not teacher:
            raise ValueError("This teacher does not exist")

        # Crear la clase
        class_data_dict = class_data.model_dump(exclude={"teacher_id"})
        new_class = Class(
            **class_data_dict,
            teacher=teacher  # type: ignore Segun Beanie, esto no puede ser None (ya validamos)
        )
        class_response = await self.class_repo.create(new_class)
        teacher.created_classes.append(class_response) # type: ignore AGREGA LA RELACION Y LA REFERENCIA 
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
        if len(class_item.enrolled_students) > 0:
            raise ValueError("No se puede eliminar una clase con estudiantes inscritos")

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
        current_time = datetime.now()
        future_classes = await self.class_repo.find_future_classes(current_time)
        
        # Filtrar solo las que tienen cupos disponibles
        available_classes = []
        for class_item in future_classes:
            if self._has_available_spots(class_item):
                available_classes.append(class_item)
        
        return available_classes

    async def get_upcoming_classes(self, days_ahead: int = 7) -> List[Class]:
        """Obtiene clases que empiezan en los próximos días"""
        current_time = datetime.now()
        future_time = current_time.replace(hour=23, minute=59, second=59) + timedelta(days=days_ahead)
        
        return await self.class_repo.find_by_date_range(current_time, future_time)

    async def search_classes_by_title(self, title: str) -> List[Class]:
        """Busca clases por título"""
        if not title or len(title.strip()) < 2:
            raise ValueError("El término de búsqueda debe tener al menos 2 caracteres")
        
        return await self.class_repo.find_by_title_pattern(title.strip())

    async def get_classes_by_price_range(self, min_price: Decimal, max_price: Decimal) -> List[Class]:
        """Obtiene clases dentro de un rango de precios"""
        if min_price < 0 or max_price < 0:
            raise ValueError("Los precios no pueden ser negativos")
        
        if min_price > max_price:
            raise ValueError("El precio mínimo no puede ser mayor al máximo")
        
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
        
        return not self._has_available_spots(class_item)

    async def can_enroll_student(self, class_id: str, student_id: str) -> tuple[bool, str]:
        """Verifica si un estudiante puede inscribirse a una clase"""
        class_item = await self.class_repo.get_by_id(class_id)
        if not class_item:
            return False, "La clase no existe"

        student = await self.auth_repo.get_student_by_id(student_id)
        if not student:
            return False, "El estudiante no existe"

        # Verificar si la clase ya pasó
        if class_item.start_date <= datetime.now():
            return False, "La clase ya ha comenzado"

        # Verificar si hay cupos disponibles
        if not self._has_available_spots(class_item):
            return False, "La clase está llena"

        # Verificar si el estudiante ya está inscrito
        if student in class_item.enrolled_students:
            return False, "El estudiante ya está inscrito en esta clase"

        return True, "Puede inscribirse"

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
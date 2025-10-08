from beanie import PydanticObjectId, WriteRules
from models.classes import Class
from models.users import Teacher, Student
from typing import List, Optional
from datetime import datetime

class ClassRepo:

    async def create(self, class_data: Class) -> Class:
        """Crea una nueva clase en la base de datos"""
        await class_data.insert(link_rule=WriteRules.WRITE)
        return class_data

    async def get_by_id(self, class_id: str) -> Class | None:
        """Obtiene una clase por su ID"""
        return await Class.get(class_id, fetch_links=True)

    async def get_all(self) -> List[Class]:
        """Obtiene todas las clases"""
        return await Class.find_all(fetch_links=True).to_list()

    async def update(self, class_item: Class) -> Class:
        """Actualiza una clase existente"""
        await class_item.save()
        return class_item

    async def delete(self, class_item: Class) -> None:
        """Elimina una clase"""
        await class_item.delete()

    async def find_by_teacher(self, teacher: Teacher) -> List[Class]:
        """Encuentra clases por profesor"""
        return await Class.find(Class.teacher == teacher, fetch_links=True).to_list()

    async def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Class]:
        """Encuentra clases en un rango de fechas"""
        return await Class.find(
            Class.start_date >= start_date,
            Class.start_date <= end_date,
            fetch_links=True
        ).to_list()

    async def find_by_title_pattern(self, pattern: str) -> List[Class]:
        """Busca clases por patrón en el título"""
        import re
        regex_pattern = re.compile(pattern, re.IGNORECASE)
        return await Class.find({"title": {"$regex": regex_pattern}}, fetch_links=True).to_list()

    async def find_by_price_range(self, min_price: float, max_price: float) -> List[Class]:
        """Encuentra clases en un rango de precios"""
        return await Class.find(
            Class.price >= min_price,
            Class.price <= max_price,
            fetch_links=True
        ).to_list()

    async def find_future_classes(self, from_date: datetime) -> List[Class]:
        """Encuentra clases futuras desde una fecha"""
        return await Class.find(Class.start_date > from_date, fetch_links=True).to_list()

# Función para dependency injection
def get_class_repo() -> ClassRepo:
    return ClassRepo()
from beanie import  WriteRules
from models.classes import Class
from models.users import Teacher, Student
from typing import List, Optional
from datetime import datetime

class ClassRepo:

    async def create(self, class_data: Class) -> Class:
        await class_data.insert(link_rule=WriteRules.WRITE)
        return class_data

    async def get_by_id(self, class_id: str) -> Class | None:
        return await Class.get(class_id, fetch_links=True)

    async def get_all(self) -> List[Class]:
        return await Class.find_all(fetch_links=True).to_list()
    
    async def get_all_future_classes(self) -> List[Class]:
        current_time = datetime.now().astimezone()
        return await Class.find(Class.start_date > current_time, fetch_links=True).to_list()

    async def update(self, class_item: Class) -> Class:
        await class_item.save()
        return class_item

    async def delete(self, class_item: Class) -> None:
        await class_item.delete()

    async def add_student(self, class_item: Class, student: Student) -> None:
        if student.id not in class_item.enrolled_students:
            class_item.enrolled_students.append(student) # type: ignore
            await class_item.save()

    async def find_by_teacher(self, teacher: Teacher) -> List[Class]:
        return await Class.find(Class.teacher == teacher, fetch_links=True).to_list()

    async def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Class]:
        return await Class.find(
            Class.start_date >= start_date,
            Class.start_date <= end_date,
            fetch_links=True
        ).to_list()

    async def find_by_title_pattern(self, pattern: str) -> List[Class]:
        
        import re
        regex_pattern = re.compile(pattern, re.IGNORECASE)
        return await Class.find({"title": {"$regex": regex_pattern}}, fetch_links=True).to_list()

    async def find_by_price_range(self, min_price: float, max_price: float) -> List[Class]:
        return await Class.find(
            Class.price >= min_price,
            Class.price <= max_price,
            fetch_links=True
        ).to_list()

    async def find_future_classes(self, from_date: datetime) -> List[Class]:
        return await Class.find(Class.start_date > from_date, fetch_links=True).to_list()

def get_class_repo() -> ClassRepo:
    return ClassRepo()
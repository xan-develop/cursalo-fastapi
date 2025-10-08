from beanie import PydanticObjectId
from models.users import Teacher

class TeacherRepo:

    async def create_teacher(self, teacher_data: Teacher) -> Teacher:
        await teacher_data.insert()
        return teacher_data

    async def get_teacher_by_id(self, teacher_id: str) -> Teacher | None:
        return await Teacher.get(teacher_id, fetch_links=True)

    async def get_teacher_by_username(self, username: str) -> Teacher | None:
        return await Teacher.find_one(Teacher.username == username, fetch_links=True)

    async def get_all_teachers(self) -> list[Teacher]:
        teachers = await Teacher.find_all(fetch_links=True).to_list()
        return teachers

    async def update_teacher(self, teacher_id: str, update_data: dict) -> Teacher | None:
        teacher = await self.get_teacher_by_id(teacher_id)
        if not teacher:
            return None
        for key, value in update_data.items():
            if hasattr(teacher, key):
                setattr(teacher, key, value)
        await teacher.save()
        return teacher

    async def delete_teacher(self, teacher_id: str) -> bool:
        teacher = await self.get_teacher_by_id(teacher_id)
        if not teacher:
            return False
        await teacher.delete()
        return True

# Función para dependency injection
def get_teacher_repo() -> TeacherRepo:
    return TeacherRepo()
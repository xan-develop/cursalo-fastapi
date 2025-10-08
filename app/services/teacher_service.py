from repositories.teacher_repo import get_teacher_repo, TeacherRepo
from models.users import Teacher

class TeacherService:
    def __init__(self, repo: TeacherRepo):
        self.repo = repo

    async def get_teacher_by_id(self, teacher_id: str) -> Teacher | None:
        return await self.repo.get_teacher_by_id(teacher_id)


    async def get_all_teachers(self) -> list[Teacher]:
        return await self.repo.get_all_teachers()

    async def delete_teacher(self, teacher_id: str) -> bool:
        return await self.repo.delete_teacher(teacher_id)

# Función para dependency injection
def get_teacher_service() -> TeacherService:
    repo = get_teacher_repo()
    return TeacherService(repo)
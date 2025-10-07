from repositories.student_repo import get_student_repo, StudentRepo
from models.users import Student

class StudentService:
    def __init__(self, repo: StudentRepo):
        self.repo = repo

    async def get_student_by_id(self, student_id: str) -> Student | None:
        return await self.repo.get_student_by_id(student_id)

    async def get_all_students(self) -> list[Student]:
        return await self.repo.get_all_students()

    async def delete_student(self, student_id: str) -> bool:
        return await self.repo.delete_student(student_id)

# Función para dependency injection
def get_student_service() -> StudentService:
    repo = get_student_repo()
    return StudentService(repo)
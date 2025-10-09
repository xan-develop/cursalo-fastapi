from repositories.student_repo import get_student_repo, StudentRepo
from models.users import Student, StudentResponse, StudentUpdate

class StudentService:
    def __init__(self, repo: StudentRepo):
        self.repo = repo

    async def get_student_by_id(self, student_id: str) -> Student | None:
        return await self.repo.get_student_by_id(student_id)

    async def get_all_students(self) -> list[Student]:
        return await self.repo.get_all_students()

    async def delete_student(self, student_id: str) -> bool:
        return await self.repo.delete_student(student_id)

    async def update_student(self, student_id: str, student_update: StudentUpdate) -> StudentResponse | None:
        # Obtener el estudiante actual
        student_data = await self.repo.get_student_by_id(student_id)
        if not student_data:
            raise ValueError("Student not found")
        
        # Obtener solo los campos que se van a actualizar
        update_fields = student_update.model_dump(exclude_unset=True, exclude_none=True)
        
        if not update_fields:
            raise ValueError("No fields to update")
        
        # Actualizar solo los campos proporcionados
        for field, value in update_fields.items():
            if hasattr(student_data, field):
                setattr(student_data, field, value)
        
        
        await self.repo.update_student(student_data)
        student_response = StudentResponse.from_student(student_data)
        return student_response
    
    async def add_voucher(self, student_id: str, amount: int) -> Student | None:
        """Agrega bonos/tickets a un estudiante"""
        student = await self.repo.get_student_by_id(student_id)
        if not student:
            raise ValueError("Student not found")
        return await self.repo.add_voucher(student, amount)

    async def decrease_voucher(self, student_id: str, amount: int) -> Student | None:
        """Disminuye bonos/tickets de un estudiante"""
        student = await self.repo.get_student_by_id(student_id)
        if not student:
            raise ValueError("Student not found")
        if student.voucher < amount:
            raise ValueError("Insufficient voucher balance")
        if amount < 0:
            raise ValueError("Amount must be positive")
        if amount == 0:
            return student  
        if amount > student.voucher:
            raise ValueError("Cannot decrease voucher below zero")
        return await self.repo.decrease_voucher(student, amount)

# Función para dependency injection
def get_student_service() -> StudentService:
    repo = get_student_repo()
    return StudentService(repo)
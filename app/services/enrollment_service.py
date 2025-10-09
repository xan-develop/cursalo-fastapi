from repositories.enrollment_repo import get_enrollment_repo, EnrollmentRepo
from repositories.class_repo import get_class_repo, ClassRepo
from repositories.student_repo import get_student_repo, StudentRepo
from models.enrollment import Enrollment, EnrollmentRequest, EnrollmentResponse
from models.classes import Class
from models.users import Student
from models.voucher_history import VoucherHistory
from fastapi import Depends, HTTPException, status
from typing import List


class EnrollmentService:
    def __init__(
        self, 
        enrollment_repo: EnrollmentRepo,
        student_repo: StudentRepo,
        class_repo: ClassRepo
    ):
        self.enrollment_repo = enrollment_repo
        self.student_repo = student_repo
        self.class_repo = class_repo

    async def create_enrollment_voucher(self, enrollment_data: EnrollmentRequest) -> EnrollmentResponse:
        """Crea una nueva inscripción usando un tocket/bono de estudiante"""
        selected_class = await self.class_repo.get_by_id(enrollment_data.class_id)
        student = await self.student_repo.get_student_by_id(enrollment_data.student_id)
        
        if not selected_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found.")
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

        try:
            await self.student_repo.decrease_voucher(student, 1)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient vouchers.") from e

        new_enrollment = Enrollment(
            student=student, # type: ignore Documentacion de beanie sobre referencias
            class_=selected_class, # type: ignore Documentacion de beanie sobre referencias
            payment_type=enrollment_data.payment_type
        )
        
        created_enrollment = await self.enrollment_repo.create_enrollment(new_enrollment)
        await self.class_repo.add_student(selected_class, student)
        await self.student_repo.add_enrolled_class(student, selected_class)
        return EnrollmentResponse.from_enrollment(created_enrollment)

    async def get_enrollments_by_student(self, student_id: str) -> List[EnrollmentResponse]:
        """Obtiene todas las inscripciones de un estudiante por su ID"""
        student = await self.student_repo.get_student_by_id(student_id)
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
        
        enrollments = await self.enrollment_repo.get_enrollments_by_student(student_id)
        return [EnrollmentResponse.from_enrollment(enrollment) for enrollment in enrollments]
    
# Función para dependencia de EnrollmentService
def get_enrollment_service() -> EnrollmentService:
    enrollment_repo = get_enrollment_repo()
    student_repo = get_student_repo()
    class_repo = get_class_repo()
    return EnrollmentService(
        enrollment_repo=enrollment_repo,
        student_repo=student_repo,
        class_repo=class_repo
    )

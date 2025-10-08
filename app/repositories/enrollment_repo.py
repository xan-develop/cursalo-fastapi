from beanie import PydanticObjectId
from app.models.enrollment import Enrollment
from models.classes import Class
from models.users import Student
from models.voucher import Voucher
from typing import List, Optional, Literal

class EnrollmentRepo:

    async def create_enrollment(self, enrollment_data: Enrollment) -> Enrollment:
        await enrollment_data.insert()
        return enrollment_data

    async def get_enrollment_by_id(self, enrollment_id: str) -> Enrollment | None:
        return await Enrollment.get(enrollment_id, fetch_links=True)

    async def get_all_enrollments(self) -> List[Enrollment]:
        enrollments = await Enrollment.find_all(fetch_links=True).to_list()
        return enrollments

    async def get_enrollments_by_student(self, student_id: str) -> List[Enrollment]:
        """Obtiene todas las inscripciones de un estudiante"""
        student = await Student.get(student_id)
        if not student:
            return []
        enrollments = await Enrollment.find(Enrollment.student == student, fetch_links=True).to_list()
        return enrollments

    async def get_enrollments_by_class(self, class_id: str) -> List[Enrollment]:
        """Obtiene todas las inscripciones de una clase"""
        class_item = await Class.get(class_id)
        if not class_item:
            return []
        enrollments = await Enrollment.find(Enrollment.class_ == class_item, fetch_links=True).to_list()
        return enrollments

    async def enroll_student(self, student_id: str, class_id: str, payment_type: Literal["direct", "voucher"], voucher_id: Optional[str] = None) -> Enrollment | None:
        """Inscribe un estudiante en una clase"""
        # Verificar que existan el estudiante y la clase
        student = await Student.get(student_id)
        class_item = await Class.get(class_id)
        
        if not student or not class_item:
            return None

        # Verificar si ya existe una inscripción
        existing_enrollment = await Enrollment.find_one(
            Enrollment.student == student,
            Enrollment.class_ == class_item
        )
        if existing_enrollment:
            return None

        # Verificar cupos disponibles si hay límite
        if class_item.max_students:
            current_enrollments = await self.get_enrollments_by_class(class_id)
            if len(current_enrollments) >= class_item.max_students:
                return None

        # Manejar voucher si se especifica
        voucher = None
        if payment_type == "voucher" and voucher_id:
            voucher = await Voucher.get(voucher_id)
            if not voucher:
                return None

        # Crear la inscripción - en Beanie los Links se pueden asignar directamente
        enrollment_data = {
            "student": student,
            "class_": class_item,
            "payment_type": payment_type
        }
        
        if voucher:
            enrollment_data["voucher_used"] = voucher
            
        enrollment = Enrollment(**enrollment_data)
        
        await enrollment.insert()
        return enrollment

    async def unenroll_student(self, student_id: str, class_id: str) -> bool:
        """Desinscribe un estudiante de una clase"""
        student = await Student.get(student_id)
        class_item = await Class.get(class_id)
        
        if not student or not class_item:
            return False

        enrollment = await Enrollment.find_one(
            Enrollment.student == student,
            Enrollment.class_ == class_item
        )
        
        if not enrollment:
            return False

        await enrollment.delete()
        return True

    async def is_student_enrolled(self, student_id: str, class_id: str) -> bool:
        """Verifica si un estudiante está inscrito en una clase"""
        student = await Student.get(student_id)
        class_item = await Class.get(class_id)
        
        if not student or not class_item:
            return False

        enrollment = await Enrollment.find_one(
            Enrollment.student == student,
            Enrollment.class_ == class_item
        )
        
        return enrollment is not None

    async def get_enrollment_count_by_class(self, class_id: str) -> int:
        """Obtiene el número de estudiantes inscritos en una clase"""
        enrollments = await self.get_enrollments_by_class(class_id)
        return len(enrollments)

    async def get_voucher_enrollments(self) -> List[Enrollment]:
        """Obtiene todas las inscripciones que usaron voucher"""
        enrollments = await Enrollment.find(
            Enrollment.payment_type == "voucher",
            fetch_links=True
        ).to_list()
        return enrollments

    async def get_direct_payment_enrollments(self) -> List[Enrollment]:
        """Obtiene todas las inscripciones con pago directo"""
        enrollments = await Enrollment.find(
            Enrollment.payment_type == "direct",
            fetch_links=True
        ).to_list()
        return enrollments

    async def delete_enrollment(self, enrollment_id: str) -> bool:
        enrollment = await self.get_enrollment_by_id(enrollment_id)
        if not enrollment:
            return False
        await enrollment.delete()
        return True

# Función para dependency injection
def get_enrollment_repo() -> EnrollmentRepo:
    return EnrollmentRepo()
from typing import Annotated, List, TYPE_CHECKING
from fastapi import APIRouter, Depends, HTTPException, status
from services.enrollment_service import EnrollmentService, get_enrollment_service
from security.auth_service import TokenData, require_role
from models.enrollment import EnrollmentRequest, EnrollmentResponse

router = APIRouter(prefix="/enrollments", tags=["enrollments"])

@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment_voucher(
    enrollment_data: EnrollmentRequest,
    enrollment_service: Annotated["EnrollmentService", Depends(get_enrollment_service)],
    user: TokenData = Depends(require_role("student"))
):
    """
    Crea una nueva inscripción para un estudiante en una clase.

    - **enrollment_data**: Datos de la inscripción a crear.
    - **enrollment_service**: Servicio de inscripción inyectado.
    - **user**: Usuario autenticado (requerido).

    Respuestas:
    - 201: Inscripción creada exitosamente.
    - 404: Clase o estudiante no encontrado.

    Excepciones:
    - HTTPException: Si la clase o el estudiante no existen.
    """
    if user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted.")
    
    return await enrollment_service.create_enrollment_voucher(enrollment_data)

@router.get("/student/{student_id}", response_model=List[EnrollmentResponse])
async def get_enrollments_by_student(
    student_id: str,
    enrollment_service: Annotated["EnrollmentService", Depends(get_enrollment_service)],
    user: TokenData = Depends(require_role("student"))
):
    """
    Obtiene todas las inscripciones de un estudiante.

    - **student_id**: ID del estudiante cuyas inscripciones se desean obtener.
    - **enrollment_service**: Servicio de inscripción inyectado.
    - **user**: Usuario autenticado (requerido).

    Respuestas:
    - 200: Lista de inscripciones del estudiante.
    - 404: Estudiante no encontrado.

    Excepciones:
    - HTTPException: Si el estudiante no existe.
    """
    if user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted.")

    return await enrollment_service.get_enrollments_by_student(student_id)

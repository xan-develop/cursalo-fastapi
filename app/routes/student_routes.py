from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from models.users import Student, StudentResponse, StudentUpdate
from services.student_service import StudentService, get_student_service
from security.auth_service import TokenData, require_role 

router = APIRouter(prefix="/students", tags=["students"])

@router.get("/{student_id}", response_model=Student)
async def get_student_by_id(
    student_id: str,
    student_service: Annotated[StudentService, Depends(get_student_service)]
):
    """
    Obtiene un estudiante por ID.

    - **student_id**: ID del estudiante.
    - **student_service**: Servicio de estudiante inyectado.

    Respuestas:
    - 200: Datos del estudiante.
    - 404: Estudiante no encontrado.
    """
    student = await student_service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.get("/", response_model=List[Student])
async def get_all_students(
    student_service: Annotated[StudentService, Depends(get_student_service)],
    user: dict = Depends(require_role("student"))
):
    """
    Obtiene todos los estudiantes.

    - **student_service**: Servicio de estudiante inyectado.

    Respuestas:
    - 200: Lista de estudiantes.
    """
    return await student_service.get_all_students()

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: str,
    student_service: Annotated[StudentService, Depends(get_student_service)]
):
    """
    Elimina un estudiante por ID.

    - **student_id**: ID del estudiante.
    - **student_service**: Servicio de estudiante inyectado.

    Respuestas:
    - 204: Eliminación exitosa.
    - 404: Estudiante no encontrado.
    """
    success = await student_service.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    
@router.patch("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    student: StudentUpdate,
    student_service: Annotated[StudentService, Depends(get_student_service)]
):
    """
    Actualiza un estudiante por ID.

    - **student_id**: ID del estudiante.
    - **student**: Datos del estudiante a actualizar.
    - **student_service**: Servicio de estudiante inyectado.

    Respuestas:
    - 200: Datos actualizados del estudiante.
    - 404: Estudiante no encontrado.
    - 400: Datos de estudiante vacíos.
    """
    updated_student = await student_service.update_student(student_id,student)
    if not updated_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated_student

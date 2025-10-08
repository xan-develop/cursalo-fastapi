from typing import Annotated, List, TYPE_CHECKING
from fastapi import APIRouter, Depends, HTTPException, status

if TYPE_CHECKING:
    from models.users import Student, StudentResponse, StudentUpdate
else:
    from models.users import Student, StudentResponse, StudentUpdate

from services.student_service import StudentService, get_student_service
from security.auth_service import require_role 

router = APIRouter(prefix="/students", tags=["students"])

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student_by_id(
    student_id: str,
    student_service: Annotated[StudentService, Depends(get_student_service)]
):
    """
    Obtiene un estudiante por ID.

    - **student_id**: ID único del estudiante a buscar.
    - **student_service**: Servicio de estudiante inyectado.

    Respuestas:
    - 200: Datos del estudiante encontrado.
    - 404: Estudiante no encontrado.

    Excepciones:
    - HTTPException: Si el estudiante no existe.
    """
    student = await student_service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentResponse.from_student(student)

@router.get("/", response_model=List[Student])
async def get_all_students(
    student_service: Annotated[StudentService, Depends(get_student_service)],
    user: dict = Depends(require_role("student"))
):
    """
    Obtiene todos los estudiantes registrados.

    - **student_service**: Servicio de estudiante inyectado.
    - **user**: Usuario autenticado con rol de estudiante (requerido).

    Respuestas:
    - 200: Lista completa de estudiantes.

    Nota:
    - Requiere autenticación con rol de estudiante.
    """
    return await student_service.get_all_students()

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: str,
    student_service: Annotated[StudentService, Depends(get_student_service)]
):
    """
    Elimina un estudiante del sistema.

    - **student_id**: ID único del estudiante a eliminar.
    - **student_service**: Servicio de estudiante inyectado.

    Respuestas:
    - 204: Eliminación exitosa.
    - 404: Estudiante no encontrado.

    Excepciones:
    - HTTPException: Si el estudiante no existe.
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
    Actualiza parcialmente los datos de un estudiante.

    - **student_id**: ID único del estudiante a actualizar.
    - **student**: Datos parciales del estudiante a modificar.
    - **student_service**: Servicio de estudiante inyectado.

    Respuestas:
    - 200: Datos actualizados del estudiante.
    - 404: Estudiante no encontrado.
    - 400: Datos de actualización inválidos.

    Excepciones:
    - HTTPException: Si el estudiante no existe o los datos son inválidos.
    """
    updated_student = await student_service.update_student(student_id,student)
    if not updated_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated_student
    

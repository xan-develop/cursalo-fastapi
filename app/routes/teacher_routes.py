from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from models.users import Teacher , TeacherResponse
from services.teacher_service import TeacherService, get_teacher_service
from security.auth_service import TokenData, require_role
router = APIRouter(prefix="/teachers", tags=["teachers"])

@router.get("/{teacher_id}", response_model=TeacherResponse)
async def get_teacher_by_id(
    teacher_id: str,
    teacher_service: Annotated[TeacherService, Depends(get_teacher_service)]
):
    """
    Obtiene un profesor por ID.

    - **teacher_id**: ID del profesor.
    - **teacher_service**: Servicio de profesor inyectado.

    Respuestas:
    - 200: Datos del profesor.
    - 404: Profesor no encontrado.
    """
    teacher = await teacher_service.get_teacher_by_id(teacher_id)
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return TeacherResponse.from_teacher(teacher)

@router.get("/", response_model=List[Teacher])
async def get_all_teachers(
    teacher_service: Annotated[TeacherService, Depends(get_teacher_service)],
    user: dict = Depends(require_role("teacher"))
):
    """
    Obtiene todos los profesores.

    - **current_user**: Usuario autenticado con rol de teacher.
    - **teacher_service**: Servicio de profesor inyectado.

    Respuestas:
    - 200: Lista de profesores.
    - 403: Acceso denegado si no es teacher.
    """
    return await teacher_service.get_all_teachers()

@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: str,
    teacher_service: Annotated[TeacherService, Depends(get_teacher_service)],
    user: dict = Depends(require_role("teacher"))
):
    """
    Elimina un profesor por ID.

    - **teacher_id**: ID del profesor.
    - **teacher_service**: Servicio de profesor inyectado.

    Respuestas:
    - 204: Eliminación exitosa.
    - 404: Profesor no encontrado.
    """
    success = await teacher_service.delete_teacher(teacher_id)
    if not success:
        raise HTTPException(status_code=404, detail="Teacher not found")
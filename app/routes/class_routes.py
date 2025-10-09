from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from models.classes import Class, ClassCreateRequest, ClassUpdateRequest , ClassResponse
from services.class_service import ClassService, get_class_service
from security.auth_service import require_role , get_current_user

router = APIRouter(prefix="/classes", tags=["classes"])

@router.post("/", response_model=ClassResponse, status_code=201)
async def create_class(
    class_request: ClassCreateRequest,
    class_service: Annotated[ClassService, Depends(get_class_service)],
    user: dict = Depends(require_role("teacher"))
):
    """
    Crea una nueva clase. Solo los profesores pueden crear clases.

    - **class_request**: Datos de la clase a crear.
    - **class_service**: Servicio de clases inyectado.

    Respuestas:
    - 201: Clase creada exitosamente.
    - 403: Sin permisos para crear clases.
    """
    try:
        created_class = await class_service.create_class(class_request)
        return ClassResponse.from_model(created_class)
    except ValueError as e:
        # Capturar el ValueError del servicio y convertirlo a HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        # Capturar cualquier otro error inesperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor al crear la clase: {str(e)}"
            
        )

@router.get("/", response_model=List[ClassResponse])
async def get_all_classes(
    class_service: Annotated[ClassService, Depends(get_class_service)],
    available_only: bool = Query(False, description="Solo mostrar clases disponibles"),
    teacher_id: Optional[str] = Query(None, description="Filtrar por ID del profesor")
):
    """
    Obtiene todas las clases con filtros opcionales.

    - **class_service**: Servicio de clases inyectado.
    - **available_only**: Si true, solo muestra clases disponibles.
    - **teacher_id**: Filtrar clases por profesor.

    Respuestas:
    - 200: Lista de clases.
    """
    try:
        if teacher_id:
            classes = await class_service.get_classes_by_teacher(teacher_id)
        elif available_only:
            classes = await class_service.get_available_classes()
        else:
            classes = await class_service.get_all_classes()

        class_response = [ClassResponse.from_model(c) for c in classes]
        return class_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener las clases"
        )

@router.get("/future", response_model=List[ClassResponse])
async def get_all_future_classes(
    class_service: Annotated[ClassService, Depends(get_class_service)],
    user: dict = Depends(get_current_user)
):
    """
    Obtiene todas las clases futuras.

    - **class_service**: Servicio de clases inyectado.

    Respuestas:
    - 200: Lista de clases futuras.
    """
    try:
        classes = await class_service.get_all_future_classes()
        class_response = [ClassResponse.from_model(c) for c in classes]
        return class_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener las clases futuras"
        )

@router.get("/{class_id}", response_model=Class)
async def get_class_by_id(
    class_id: str,
    class_service: Annotated[ClassService, Depends(get_class_service)]
):
    """
    Obtiene una clase por ID.

    - **class_id**: ID de la clase.
    - **class_service**: Servicio de clases inyectado.

    Respuestas:
    - 200: Datos de la clase.
    - 404: Clase no encontrada.
    """
    try:
        class_item = await class_service.get_class_by_id(class_id)
        if not class_item:
            raise HTTPException(status_code=404, detail="Clase no encontrada")
        return class_item
    except HTTPException:
        # Re-raise HTTPExceptions para que mantengan su status code
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener la clase"
        )

@router.put("/{class_id}", response_model=Class)
async def update_class(
    class_id: str,
    update_data: ClassUpdateRequest,
    class_service: Annotated[ClassService, Depends(get_class_service)],
    user: dict = Depends(require_role("teacher"))
):
    """
    Actualiza una clase existente.

    - **class_id**: ID de la clase a actualizar.
    - **update_data**: Nuevos datos para la clase.
    - **class_service**: Servicio de clases inyectado.

    Respuestas:
    - 200: Clase actualizada exitosamente.
    - 404: Clase no encontrada.
    """
    try:
        updated_class = await class_service.update_class(class_id, update_data)
        if not updated_class:
            raise HTTPException(status_code=404, detail="Clase no encontrada")
        return updated_class
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar la clase"
        )

@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(
    class_id: str,
    class_service: Annotated[ClassService, Depends(get_class_service)],
    user: dict = Depends(require_role("teacher"))
):
    """
    Elimina una clase.

    - **class_id**: ID de la clase a eliminar.
    - **class_service**: Servicio de clases inyectado.

    Respuestas:
    - 204: Clase eliminada exitosamente.
    - 404: Clase no encontrada.
    """
    try:
        success = await class_service.delete_class(class_id)
        if not success:
            raise HTTPException(status_code=404, detail="Clase no encontrada")
    except HTTPException:
        raise
    except ValueError as e:
        # Manejar errores de validación (ej: clase con estudiantes inscritos)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar la clase"
        )


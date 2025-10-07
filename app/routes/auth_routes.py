from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.users import Teacher, TeacherRegistration , StudentRegistration, User
from security.auth_service import (
    AuthService,
    get_auth_service,
    get_current_user, 
    Token, 
    TokenData,
)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register/teacher", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_teacher(
    teacher_data: TeacherRegistration,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Registra una nueva cuenta de profesor.

    - **teacher_data**: Datos de registro del profesor (TeacherRegistration).
    - **auth_service**: Servicio de autenticación inyectado.

    Respuestas:
    - 201: Cuenta creada exitosamente, devuelve mensaje, ID, username y email.
    - 500: Error interno al crear la cuenta.

    Excepciones:
    - HTTPException: Si ocurre un error específico durante el registro.
    """
    try:
        teacher = await auth_service.create_teacher_account(teacher_data)
        return {
            "message": "Teacher account created successfully",
            "teacher_id": str(teacher.id),
            "username": teacher.username,
            "email": teacher.email
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating teacher account: {str(e)}"
        )

@router.post("/register/student", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_student(
    student_data: StudentRegistration,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Registra una nueva cuenta de estudiante.

    - **student_data**: Datos de registro del estudiante (StudentRegistration).
    - **auth_service**: Servicio de autenticación inyectado.

    Respuestas:
    - 201: Cuenta creada exitosamente, devuelve mensaje, ID, username y email.
    - 500: Error interno al crear la cuenta.

    Excepciones:
    - HTTPException: Si ocurre un error específico durante el registro.
    """
    try:
        student = await auth_service.create_student_account(student_data)
        return {
            "message": "Student account created successfully",
            "student_id": str(student.id),
            "username": student.username,
            "email": student.email
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating student account: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Inicia sesión de un usuario y devuelve un token de acceso.

    - **form_data**: Datos del formulario de login (username y password).
    - **auth_service**: Servicio de autenticación inyectado.

    Respuestas:
    - 200: Token de acceso generado.
    - 500: Error interno durante el login.

    Excepciones:
    - HTTPException: Si las credenciales son inválidas o ocurre un error.
    """
    try:
        token = await auth_service.login_user(form_data.username, form_data.password)
        return token
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}"
        )

@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: Annotated[TokenData, Depends(get_current_user)]
):
    """
    Obtiene la información del usuario actualmente autenticado.

    - **current_user**: Datos del usuario actual (TokenData).

    Respuestas:
    - 200: Información del usuario (ID, username, email, role).
    """
    return {
        "user_id": current_user.sub,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }

@router.get("/users", response_model=list[dict])
async def get_all_users(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    current_user: Annotated[TokenData, Depends(get_current_user)]
):
    """
    Obtiene una lista de todos los usuarios registrados.

    - **auth_service**: Servicio de autenticación inyectado.

    Respuestas:
    - 200: Lista de usuarios con detalles (ID, username, email, etc.).
    - 500: Error interno al obtener usuarios.
    """
    try:
        users = await auth_service.get_all_users()
        return [
            {
                "user_id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "__class__": user.__class__.__name__
            }
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )
@router.patch("/update-password", response_model=dict)
async def update_password(
    new_password: str,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Actualiza la contraseña del usuario actualmente autenticado.

    - **new_password**: Nueva contraseña (mínimo 6 caracteres).
    - **current_user**: Datos del usuario actual (TokenData).
    - **auth_service**: Servicio de autenticación inyectado.

    Respuestas:
    - 200: Contraseña actualizada exitosamente.
    - 400: Contraseña inválida o usuario no autorizado.
    - 500: Error interno al actualizar.

    Excepciones:
    - HTTPException: Si la contraseña es demasiado corta o el usuario es inválido.
    """
    if not new_password or len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long"
        )
    if not current_user or not current_user.sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user"
        )
    try:
        await auth_service.update_password(current_user.sub, new_password)
        return {"message": f"Password updated successfully for user: {current_user.username}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating password: {str(e)}"
        )
        
@router.post("/recovery-password", response_model=dict)
async def create_recovery_password_token(
    email: str,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Crea un token de recuperación de contraseña para un usuario por email.

    - **email**: Email del usuario.
    - **auth_service**: Servicio de autenticación inyectado.

    Respuestas:
    - 200: Token de recuperación creado.
    - 404: Usuario no encontrado.
    - 500: Error interno al generar el token.

    Excepciones:
    - HTTPException: Si el email no existe o hay error en la generación.
    """
    try:
        user = await auth_service.auth_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email does not exist"
            )
        token = await auth_service.create_recovery_password_token(str(user.id))
        if not token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating recovery token"
            )
        return {
            "message": "Recovery password token created successfully",
            "recovery_token": token
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating recovery password token: {str(e)}"
        )
        
@router.post("/reset-password", response_model=dict)
async def reset_password(
    token: str,
    new_password: str,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Restablece la contraseña usando un token de recuperación.

    - **token**: Token de recuperación válido.
    - **new_password**: Nueva contraseña (mínimo 6 caracteres).
    - **auth_service**: Servicio de autenticación inyectado.

    Respuestas:
    - 200: Contraseña restablecida exitosamente.
    - 400: Token inválido, tipo incorrecto o contraseña demasiado corta.
    - 500: Error interno al restablecer.

    Excepciones:
    - HTTPException: Si el token es inválido o hay error en la verificación.
    """
    if not new_password or len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long"
        )
    try:
        payload = await auth_service.verify_token(token)
        if payload.get("type") != "recovery_password":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type"
            )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload"
            )
        await auth_service.update_password(user_id, new_password)
        return {"message": "Password has been reset successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting password: {str(e)}"
        )

@router.post("/create-initial-admin", response_model=User)
async def create_initial_admin_user(password: str, auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    """
    Crea un usuario administrador inicial si no existe.

    - **auth_service**: Servicio de autenticación inyectado.

    Este usuario tendrá las siguientes credenciales:
    - Username: admin
    - Email: admin@example.com
    - Password: admin_password
    """
    # Verificar si el usuario ya existe
    existing_user = await auth_service.auth_repo.get_user_by_email("admin@example.com")
    if existing_user:
        return existing_user

    # Crear el usuario administrador
    admin_user = await auth_service.create_admin_user(password)
    return admin_user

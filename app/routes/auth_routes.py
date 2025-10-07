from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.users import Teacher, TeacherRegistration , StudentRegistration
from security.auth_service import (
    AuthService,
    get_auth_service,
    get_current_user, 
    Token, 
    TokenData
)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register/teacher", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_teacher(
    teacher_data: TeacherRegistration,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
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

    return {
        "user_id": current_user.sub,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }

@router.get("/users", response_model=list[dict])
async def get_all_users(
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
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
        return {"message": "Password updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating password: {str(e)}"
        )

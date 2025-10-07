from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from models.users import Teacher, TeacherRegistration, User , StudentRegistration , Student
from repositories.auth_repo import get_auth_repo, AuthRepo

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class TokenData(BaseModel):
    sub: str | None = None
    username: str | None = None
    email: str | None = None
    role: str | None = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
password_hash = PasswordHash.recommended()

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=encoded_jwt, token_type="bearer")

def create_recovery_pass_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



class AuthService:
    """Servicio centralizado para operaciones de autenticación"""
    
    def __init__(self, auth_repo: AuthRepo):
        self.auth_repo = auth_repo

    async def create_teacher_account(self, teacher_data: TeacherRegistration) -> Teacher:
        """Crea una nueva cuenta de profesor"""
        # Validaciones
        if await self.auth_repo.get_user_by_email(teacher_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        if await self.auth_repo.get_user_by_username(teacher_data.username):
            raise HTTPException(status_code=400, detail="Username already taken")
        if not teacher_data.password:
            raise HTTPException(status_code=400, detail="Password cannot be empty")
        
        # Hashear contraseña y crear profesor
        hashed_password = get_password_hash(teacher_data.password)
        teacher_dict = teacher_data.model_dump()
        teacher_dict["password"] = hashed_password
        new_teacher = Teacher(**teacher_dict)
        new_teacher.role = "teacher"
        
        # Guardar en base de datos
        teacher = await self.auth_repo.create_teacher(new_teacher)
        return teacher

    async def create_student_account(self, student_data: StudentRegistration) -> Student:
        """Crea una nueva cuenta de estudiante"""
        # Validaciones
        if await self.auth_repo.get_user_by_email(student_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        if await self.auth_repo.get_user_by_username(student_data.username):
            raise HTTPException(status_code=400, detail="Username already taken")
        if not student_data.password:
            raise HTTPException(status_code=400, detail="Password cannot be empty")
        
        # Hashear contraseña y crear estudiante
        hashed_password = get_password_hash(student_data.password)
        student_dict = student_data.model_dump()
        student_dict["password"] = hashed_password
        new_student = Student(**student_dict)
        new_student.role = "student"
        
        # Guardar en base de datos
        student = await self.auth_repo.create_student(new_student)
        return student
    
    async def login_user(self, username: str, password: str) -> Token:
        """Autentica un usuario y devuelve un token de acceso"""
        user = await self.auth_repo.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}, 
            expires_delta=access_token_expires
        )
        return access_token

    async def log_out_user(self, token: str) -> None:
        """Cierra la sesión de un usuario (simulado)"""
        # En un sistema real, se podría implementar una lista de tokens revocados
        pass

    async def get_user_by_username(self, username: str) -> User | None:
        """Obtiene un usuario por su nombre de usuario"""
        return await self.auth_repo.get_user_by_username(username)

    async def get_current_user_from_token(self, token: str) -> TokenData:
        """Obtiene el usuario actual desde un token JWT"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("email")
            sub: str = payload.get("sub")
            if email is None:
                raise credentials_exception
                
            # Verificar que el usuario existe en la base de datos
            user = await self.auth_repo.get_user_by_email(email)
            if user is None:
                raise credentials_exception
                
            token_data = TokenData(
                sub=sub,
                username=user.username,
                email=user.email, 
                role=user.role
            )
        except InvalidTokenError:
            raise credentials_exception
        return token_data
    
    async def get_all_users(self) -> list[User]:
        """Obtiene todos los usuarios"""
        return await self.auth_repo.get_all_users()
    
    async def verify_token(self, token: str) -> dict:
        """Verifica la validez de un token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("exp") < datetime.now(timezone.utc).timestamp():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return payload
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    async def verify_role(self, token: str, required_role: str) -> bool:
        """Verifica si el usuario tiene el rol requerido"""
        payload = await self.verify_token(token)
        user_role = payload.get("role")
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted",
            )
        return True
            
    async def update_password(self, user_id: str, new_password: str) -> None:
        """Actualiza la contraseña de un usuario"""
        new_hashed_password = get_password_hash(new_password)
        await self.auth_repo.update_password(user_id, new_hashed_password)

    async def create_recovery_password_token(self, user_id: str) -> str | None:
        """Crea un token de recuperación de contraseña"""
        user = await self.auth_repo.get_user_by_id(user_id)
        if not user:
            return None
        token = create_recovery_pass_token({"sub": str(user.id) , "email": user.email , "role": user.role , "expedition_date": datetime.now(timezone.utc).timestamp() , "type": "recovery_password"})
        return token
    
    async def create_admin_user(self, password: str) -> User:
        """Crea un usuario administrador si no existe"""
        existing_user = await self.auth_repo.get_user_by_username("admin")
        if existing_user:
            return existing_user
        
        hashed_password = get_password_hash(password)
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password=hashed_password,
            role="admin"
        )
        return await self.auth_repo.create_user(admin_user)

# Función para obtener una instancia de AuthService
def get_auth_service(auth_repo: Annotated[AuthRepo, Depends(get_auth_repo)]) -> AuthService:
    return AuthService(auth_repo)

# Función para obtener el usuario actual usando AuthService
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> TokenData:
    return await auth_service.get_current_user_from_token(token)

def require_role(role: str):
    def role_checker(user: TokenData = Depends(get_current_user)):
        if user.role != role and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your role has forbidden access to this resource",
            )
        return user
    return role_checker

async def get_user_role(current_user: Annotated[TokenData, Depends(get_current_user)]):
    return current_user.role


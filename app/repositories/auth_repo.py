from datetime import timedelta
from beanie import PydanticObjectId
from pydantic import ValidationError
from models.users import User, Teacher, Student

class AuthRepo:

    async def get_user_by_username(self, username: str) -> User | None:
        return await User.find_one(User.username == username , with_children=True)

    async def get_user_by_email(self, email: str) -> User | None:
        return await User.find_one(User.email == email , with_children=True)

    async def get_user_by_id(self, user_id: str) -> User | None:
        try:
            return await User.get(user_id , with_children=True)
        except Exception:
            return None

    async def get_teacher_by_id(self, teacher_id: str) -> Teacher | None:
        try:
            return await Teacher.get(teacher_id)
        except Exception:  # Capturar TODAS las excepciones
            return None

    async def get_student_by_id(self, student_id: str) -> Student | None:
        try:
            return await Student.get(student_id)
        except Exception:  # Capturar TODAS las excepciones
            return None

    async def create_teacher(self, teacher_data: Teacher) -> Teacher:
        await teacher_data.insert()
        return teacher_data
    
    async def create_student(self, student_data: Student) -> Student:
        await student_data.insert()
        return student_data
    
    async def create_user(self, user_data: User) -> User:
        await user_data.insert()
        return user_data
    
    async def get_all_users(self) -> list[User]:
        users = await User.find_all(with_children=True).to_list()
        return users

    async def update_password(self, user_id: str, new_hashed_password: str) -> None:
        try:
            user_data = await self.get_user_by_id(user_id)
            if not user_data:
                raise ValueError("User not found")
            user_data.password = new_hashed_password
            await user_data.save()
        except Exception as e:
            raise ValueError(f"Error updating password: {str(e)}") from e

# Función para dependency injection
def get_auth_repo() -> AuthRepo:
    return AuthRepo()

from datetime import timedelta
from models.users import User, Teacher, Student

class AuthRepo:

    async def get_user_by_username(self, username: str) -> User | None:
        return await User.find_one(Teacher.username == username , with_children=True)

    async def get_user_by_email(self, email: str) -> User | None:
        return await User.find_one(Teacher.email == email , with_children=True)

    async def get_user_by_id(self, user_id: str) -> User | None:
        return await User.find_one(Teacher.id == user_id , with_children=True)
    
    async def create_teacher(self, teacher_data: Teacher) -> Teacher:
        await teacher_data.insert()
        return teacher_data
    async def get_all_users(self) -> list[User]:
        users = await User.find_all(with_children=True).to_list()
        return users

# Función para dependency injection
def get_auth_repo() -> AuthRepo:
    return AuthRepo()

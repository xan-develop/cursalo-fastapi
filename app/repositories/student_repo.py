from beanie import PydanticObjectId
from models.classes import Class
from models.users import Student

class StudentRepo:

    async def create_student(self, student_data: Student) -> Student:
        await student_data.insert()
        return student_data

    async def get_student_by_id(self, student_id: str) -> Student | None:
        return await Student.get(student_id)

    async def get_student_by_username(self, username: str) -> Student | None:
        return await Student.find_one(Student.username == username, with_children=True)

    async def get_all_students(self) -> list[Student]:
        students = await Student.find_all(with_children=True).to_list()
        return students
    
    async def add_enrolled_class(self, student: Student, class_obj: Class) -> Student:
        if class_obj.id not in student.enrolled_classes:
            student.enrolled_classes.append(class_obj) # type: ignore
            await student.save()
        return student

    async def update_student(self, student: Student) -> Student | None:
        await student.save()
        return student
    
    async def add_voucher(self, student: Student, amount: int) -> Student:
        student.voucher += amount
        await student.save()
        return student
    
    async def decrease_voucher(self, student: Student, amount: int) -> Student:
        if student.voucher >= amount:
            student.voucher -= amount
            await student.save()
        return student
    
    

    async def delete_student(self, student_id: str) -> bool:
        student = await self.get_student_by_id(student_id)
        if not student:
            return False
        await student.delete()
        return True

# Función para dependency injection
def get_student_repo() -> StudentRepo:
    return StudentRepo()
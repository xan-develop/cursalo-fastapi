from pymongo import AsyncMongoClient
from models.users import User, Teacher, Student
from models.classes import Class
from models.voucher import Voucher
from models.enrrolment import Enrollment
from beanie import init_beanie
from config.consolelog import logger
    
async def init():
    try:
        client = AsyncMongoClient("mongodb://localhost:27017")
        await init_beanie(
            database=client.cursalo, 
            document_models=[User, Teacher, Student, Class, Voucher, Enrollment]
        )
        logger.info("Beanie inicializado correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar Beanie: {e}")
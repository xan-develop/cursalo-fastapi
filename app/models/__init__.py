"""
Inicialización de modelos para resolver referencias circulares
"""
from config.consolelog import logger

def rebuild_models():
    """
    Reconstruye los modelos después de que todas las clases estén definidas
    para resolver las referencias circulares
    """
    try:
        from models.users import Teacher, Student, User
        from models.classes import Class  # Cuando exista
        from models.voucher_history import VoucherHistory  # Cuando exista
        from models.enrollment import Enrollment  # Cuando exista
        
        # Reconstruir modelos
        User.model_rebuild()
        Teacher.model_rebuild()
        Student.model_rebuild()
        Class.model_rebuild()
        VoucherHistory.model_rebuild()
        Enrollment.model_rebuild()
        
        logger.info("✅ Todos los modelos reconstruidos correctamente")
        
    except ImportError as e:
        logger.warning(f"⚠️  Algunos modelos no están disponibles aún: {e}")
        # Solo reconstruir los modelos que sí existen
        from models.users import Teacher, Student, User
        User.model_rebuild()
        Teacher.model_rebuild() 
        Student.model_rebuild()
        logger.info("✅ Modelos de usuario reconstruidos")
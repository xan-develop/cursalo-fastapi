"""
Inicialización de modelos para resolver referencias circulares
"""

def rebuild_models():
    """
    Reconstruye los modelos después de que todas las clases estén definidas
    para resolver las referencias circulares
    """
    try:
        from models.users import Teacher, Student, User
        from models.classes import Class  # Cuando exista
        from models.voucher import Voucher  # Cuando exista
        
        # Reconstruir modelos
        User.model_rebuild()
        Teacher.model_rebuild()
        Student.model_rebuild()
        
        print("✅ Modelos reconstruidos correctamente")
        
    except ImportError as e:
        print(f"⚠️  Algunos modelos no están disponibles aún: {e}")
        # Solo reconstruir los modelos que sí existen
        from models.users import Teacher, Student, User
        User.model_rebuild()
        Teacher.model_rebuild() 
        Student.model_rebuild()
        print("✅ Modelos de usuario reconstruidos")
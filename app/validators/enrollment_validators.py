
class EnrollmentValidator:
    @staticmethod
    def validate_enrollment_data(data):
        required_fields = ["student_id", "class_id", "enrollment_date"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"El campo '{field}' es obligatorio.")
        # Validar que student_id y class_id sean cadenas no vacías
        if not isinstance(data["student_id"], str) or not data["student_id"].strip():
            raise ValueError("El 'student_id' debe ser una cadena no vacía.")
        if not isinstance(data["class_id"], str) or not data["class_id"].strip():
            raise ValueError("El 'class_id' debe ser una cadena no vacía.")
        # Validar que enrollment_date sea una fecha válida (puede ser una cadena en formato ISO)
        from datetime import datetime
        try:
            datetime.fromisoformat(data["enrollment_date"])
        except ValueError:
            raise ValueError("El 'enrollment_date' debe ser una fecha en formato ISO (YYYY-MM-DD).")
        return True
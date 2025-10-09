
class EnrollmentValidator:
    @staticmethod
    def validate_enrollment_data(data):
        required_fields = ["student_id", "class_id", "enrollment_date"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"The field '{field}' is required.")
        # Validar que student_id y class_id sean cadenas no vacías
        if not isinstance(data["student_id"], str) or not data["student_id"].strip():
            raise ValueError("The 'student_id' must be a non-empty string.")
        if not isinstance(data["class_id"], str) or not data["class_id"].strip():
            raise ValueError("The 'class_id' must be a non-empty string.")
        # Validar que enrollment_date sea una fecha válida
        from datetime import datetime
        try:
            datetime.fromisoformat(data["enrollment_date"])
        except ValueError:
            raise ValueError("The 'enrollment_date' must be a valid date.")
        return True
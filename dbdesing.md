xan-develop: genera un markdown con el diseño de base de datos de mi app

Workspace: Recopilando información del área de trabajo# Diseño de Base de Datos - App Cursalo

## 📋 Resumen General

Esta aplicación utiliza **MongoDB** como base de datos NoSQL con **Beanie ODM** para el mapeo objeto-documento. El diseño sigue un patrón de herencia para usuarios y utiliza referencias (Links) para las relaciones entre documentos.

## 🏗️ Arquitectura de Documentos

### Colecciones Principales

1. **users** - Almacena usuarios base y especializados (herencia)
2. **classes** - Información de las clases/cursos
3. **vouchers** - Vouchers de crédito para estudiantes
4. **enrollments** - Inscripciones de estudiantes en clases

## 📊 Esquema de Documentos

### 1. Collection: `users`

Utiliza herencia discriminada con el campo `role` como discriminador.

#### Documento Base: `User`
```javascript
{
  "_id": ObjectId,
  "username": String,              // ✅ Indexado - Único
  "email": String,                 // ✅ Indexado - Único  
  "full_name": String | null,
  "password": String,              // Hash bcrypt
  "role": String,                  // ✅ Indexado - "teacher" | "student" | "admin"
  "created_at": DateTime,
  "is_active": Boolean
}
```

#### Especialización: `Teacher` (role: "teacher")
```javascript
{
  // ... campos de User ...
  "role": "teacher",
  "biography": String | null,
  "specialization": String | null,
  "created_classes": [             // Array de referencias Link
    {
      "$ref": "classes",
      "$id": ObjectId
    }
  ]
}
```

#### Especialización: `Student` (role: "student")
```javascript
{
  // ... campos de User ...
  "role": "student",
  "vouchers": [                    // Array de referencias Link
    {
      "$ref": "vouchers", 
      "$id": ObjectId
    }
  ],
  "enrolled_classes": [            // Array de referencias Link
    {
      "$ref": "classes",
      "$id": ObjectId
    }
  ]
}
```

### 2. Collection: `classes`

```javascript
{
  "_id": ObjectId,
  "title": String,
  "description": String | null,
  "teacher": {                     // Referencia Link al Teacher
    "$ref": "users",
    "$id": ObjectId
  },
  "price": Decimal128,             // Precio en formato MongoDB Decimal
  "allow_voucher": Boolean,        // Si acepta vouchers
  "max_students": Number | null,   // Límite de estudiantes (null = sin límite)
  "start_date": DateTime,
  "duration_minutes": Number,
  "created_at": DateTime,
  "enrolled_students": [           // Array de referencias Link a Students
    {
      "$ref": "users",
      "$id": ObjectId
    }
  ]
}
```

### 3. Collection: `vouchers`

```javascript
{
  "_id": ObjectId,
  "student": {                     // Referencia Link al Student propietario
    "$ref": "users",
    "$id": ObjectId
  },
  "total_credits": Number,         // Créditos totales del voucher
  "remaining_credits": Number,     // Créditos restantes
  "price": Number,                 // Precio pagado por el voucher
  "created_at": DateTime,
  "expires_at": DateTime | null    // Fecha de expiración (opcional)
}
```

### 4. Collection: `enrollments`

```javascript
{
  "_id": ObjectId,
  "student": {                     // Referencia Link al Student
    "$ref": "users",
    "$id": ObjectId
  },
  "class_": {                      // Referencia Link a la Class
    "$ref": "classes", 
    "$id": ObjectId
  },
  "payment_type": String,          // "direct" | "voucher"
  "voucher_used": {                // Referencia Link al Voucher (opcional)
    "$ref": "vouchers",
    "$id": ObjectId
  } | null,
  "enrolled_at": DateTime
}
```

## 🔗 Diagrama de Relaciones

```mermaid
erDiagram
    User ||--o{ Teacher : "herencia"
    User ||--o{ Student : "herencia"
    
    Teacher ||--o{ Class : "crea/imparte"
    Student }o--o{ Class : "se inscribe"
    Student ||--o{ Voucher : "posee"
    Student ||--o{ Enrollment : "realiza"
    
    Class ||--o{ Enrollment : "tiene inscripciones"
    Voucher ||--o{ Enrollment : "usado en"
    
    User {
        ObjectId _id PK
        String username UK
        String email UK
        String role "teacher|student|admin"
        String password
        DateTime created_at
        Boolean is_active
    }
    
    Teacher {
        String biography
        String specialization
        Array created_classes "Link[]"
    }
    
    Student {
        Array vouchers "Link[]"
        Array enrolled_classes "Link[]"
    }
    
    Class {
        ObjectId _id PK
        String title
        String description
        Link teacher FK
        Decimal128 price
        Boolean allow_voucher
        Number max_students
        DateTime start_date
        Number duration_minutes
        Array enrolled_students "Link[]"
    }
    
    Voucher {
        ObjectId _id PK
        Link student FK
        Number total_credits
        Number remaining_credits
        Number price
        DateTime created_at
        DateTime expires_at
    }
    
    Enrollment {
        ObjectId _id PK
        Link student FK
        Link class_ FK
        String payment_type "direct|voucher"
        Link voucher_used FK
        DateTime enrolled_at
    }
```

## 📋 Índices de Base de Datos

### Colección `users`
```javascript
// Índices automáticos de Beanie
db.users.createIndex({ "username": 1 }, { unique: true })
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "role": 1 })

// Índice compuesto útil para búsquedas
db.users.createIndex({ "role": 1, "is_active": 1 })
```

### Colección `classes`
```javascript
// Índices recomendados para rendimiento
db.classes.createIndex({ "teacher": 1 })
db.classes.createIndex({ "start_date": 1 })
db.classes.createIndex({ "price": 1 })
db.classes.createIndex({ "title": "text" })  // Para búsqueda de texto
```

### Colección `enrollments`
```javascript
// Índices para consultas comunes
db.enrollments.createIndex({ "student": 1 })
db.enrollments.createIndex({ "class_": 1 })
db.enrollments.createIndex({ "student": 1, "class_": 1 }, { unique: true })  // Un estudiante no puede inscribirse dos veces
```

### Colección `vouchers`
```javascript
// Índices para vouchers
db.vouchers.createIndex({ "student": 1 })
db.vouchers.createIndex({ "expires_at": 1 })
```

## 🔄 Patrones de Consulta Comunes

### 1. Obtener clases de un profesor con estudiantes inscritos
```python
# En ClassRepo.find_by_teacher()
classes = await Class.find(Class.teacher == teacher, fetch_links=True).to_list()
```

### 2. Verificar inscripción de estudiante
```python
# En EnrollmentRepo.is_student_enrolled()
enrollment = await Enrollment.find_one(
    Enrollment.student == student,
    Enrollment.class_ == class_item
)
```

### 3. Buscar clases disponibles
```python
# En ClassService.get_available_classes()
future_classes = await Class.find(
    Class.start_date > datetime.now(),
    fetch_links=True
).to_list()
```

## ⚡ Consideraciones de Rendimiento

### ✅ Optimizaciones Implementadas
- **Índices estratégicos** en campos de búsqueda frecuente
- **fetch_links=True** solo cuando se necesitan las referencias
- **with_children=True** para herencia de usuarios
- **Validadores Pydantic** para conversión Decimal128 ↔ Decimal

### 📊 Métricas Esperadas
- **Usuarios**: ~10K documentos
- **Clases**: ~1K documentos activos
- **Inscripciones**: ~50K documentos
- **Vouchers**: ~5K documentos

## 🔒 Seguridad de Datos

### Validaciones a Nivel de Aplicación
- ✅ Contraseñas hasheadas con **pwdlib**
- ✅ Validación de unicidad de email/username
- ✅ Verificación de cupos en inscripciones
- ✅ Validación de fechas (clases futuras)
- ✅ Autorización por roles (teacher/student/admin)

### Integridad Referencial
- ✅ Links verificados antes de creación
- ✅ Cascada manual en eliminaciones críticas
- ✅ Validación de existencia de referencias

## 📈 Escalabilidad

### Estrategias de Crecimiento
1. **Particionamiento** por fecha de creación de clases
2. **Índices compuestos** para consultas complejas
3. **Agregaciones MongoDB** para reportes
4. **Caché Redis** para sesiones de usuario (futuro)

## 🛠️ Stack Tecnológico

- **Base de Datos**: MongoDB 7.x
- **ODM**: Beanie (basado en Pydantic + Motor)
- **Backend**: FastAPI + Python 3.11+
- **Validación**: Pydantic v2
- **Autenticación**: JWT + OAuth2

---

*Este diseño está optimizado para un sistema de gestión de clases online con vouchers de crédito, manteniendo flexibilidad para futuras expansiones.*
# Aplicación de Notas – Explicación Técnica

El proyecto está dividido en dos grandes partes: frontend y backend.
Esta separación permite mantener responsabilidades claras y facilita una futura migración a web.

## Backend
El backend sigue un enfoque basado en Clean Architecture, organizado en tres capas:

### 1. Dominio
Contiene modelos ricos en reglas de negocio.
Esta capa es completamente independiente y no depende de frameworks ni detalles técnicos.

### 2. Aplicación
Define los casos de uso, los cuales coordinan los modelos del dominio para ejecutar acciones del sistema.
Cada caso de uso:
. Devuelve un resultado explícito (éxito o error).
. Evita el uso de excepciones como mecanismo de control de flujo.
. Se utilizan DTOs para exponer datos sin filtrar modelos internos del dominio.
. Los casos de uso están envueltos por un decorador.
  Este valida tipos de entrada con Pydantic y clasifica  errores en:
  . Errores de dominio
  . Errores de persistencia
  . Errores inesperados

### 3. Infraestructura
Se encarga de la persistencia y detalles técnicos.
Se utiliza SQLAlchemy para mejorar la detección y trazabilidad de errores relacionados con la base de datos.
La base de datos es SQLite, elegida por tratarse de una aplicación de escritorio.

## Frontend
El frontend sigue un enfoque orientado a features.
Cada feature:
. vive de forma independiente no conoce directamente a las demás
. La comunicación se realiza mediante un sistema de eventos (Pub/Sub).

### Sistema de eventos
. Las features pueden suscribirse a eventos.
. Cualquier feature puede emitir eventos.
. El emisor no conoce a los receptores.

Esto permite:
. Bajo acoplamiento.
. Reutilización de features.


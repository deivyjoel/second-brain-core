# Notes Application – Technical Explanation
The project is divided into two main parts: frontend and backend.
This separation allows for clear responsibilities and facilitates a future migration to the web.

## Backend
The backend follows a Clean Architecture–based approach, organized into three layers:

### 1. Domain
Contains models rich in business rules.
This layer is completely independent and does not rely on frameworks or technical details.

### 2. Application
Defines the use cases, which coordinate the domain models to execute system actions.
Each use case:
. Returns an explicit result (success or error).
. Avoids using exceptions as a flow-control mechanism.
. Uses DTOs to expose data without leaking internal domain models.
. Use cases are wrapped by a decorator.
  This decorator validates input types with Pydantic and classifies errors into:
  . Domain errors
  . Persistence errors
  . Unexpected errors

### 3. Infrastructure
Handles persistence and technical details.
SQLAlchemy is used to improve detection and traceability of database-related errors.
The database is SQLite, chosen because this is a desktop application.

## Frontend
The frontend follows a feature-oriented approach.
Each feature:
. Lives independently and does not directly know about others.
. Communication is handled through an event system (Pub/Sub).

### Event system
. Features can subscribe to events.
. Any feature can emit events.
. The emitter does not know the receivers.

This enables:
. Low coupling.
. Feature reuse.

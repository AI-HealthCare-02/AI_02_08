# Directory Structure

## Root
- `/backend`: FastAPI backend application.
- `/frontend`: React/Vite frontend application.
- `/data`: Persistent data storage (e.g., MySQL data).

## Backend (`/backend`)
- `/app`: Core application code.
  - `/apis`: Endpoint routers.
  - `/services`: Business logic modules.
  - `/repositories`: Data access layer.
  - `/models`: Database schema definitions.
  - `/dtos`: Data Transfer Objects (Pydantic).
  - `/core`: Config, security, and logging.
  - `/db`: Database setup and migrations.
- `/ai_worker`: Dedicated worker for AI-related tasks.
- `/tests`: Pytest suite.
- `/scripts`: Utility scripts (e.g., seeding, deployment).
- `/envs`: Environment configuration files.

## Frontend (`/frontend`)
- `/src`: Application source code.
  - `/pages`: View components.
  - `/components`: UI building blocks.
  - `/api`: Backend communication services.
  - `/hooks`: Custom React logic.
  - `/routes`: React Router configuration.
  - `/types`: TypeScript definitions.
  - `/assets`: Images and styles.
- `/public`: Static assets.

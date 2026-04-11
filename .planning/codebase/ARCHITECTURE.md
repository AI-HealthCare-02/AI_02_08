# System Architecture

## Overview
The system is a decoupled web application with a FastAPI backend and a React/Vite frontend. It uses a microservice-ready directory structure but currently operates within a monorepo setup.

## Backend Architecture
The backend follows a **Layered Architecture**:
1. **API Layer (`app/apis`)**: Handles HTTP requests, authentication, and routing.
2. **Service Layer (`app/services`)**: Contains business logic and orchestrates data flow between repositories and external APIs.
3. **Repository Layer (`app/repositories`)**: Encapsulates data access logic using Tortoise ORM.
4. **Model Layer (`app/models`)**: Defines the database schema and ORM models.
5. **DTO Layer (`app/dtos`)**: Pydantic models for data validation and API responses.

## Frontend Architecture
The frontend follows a **Feature-Based/Component-Based Architecture**:
1. **Pages (`src/pages`)**: Top-level page components.
2. **Components (`src/components`)**: Reusable UI elements.
3. **API (`src/api`)**: Service modules for communicating with the backend.
4. **Hooks (`src/hooks`)**: Custom logic encapsulated in React hooks.
5. **Routes (`src/routes`)**: Navigation and routing logic.

## Data Flow
1. User interacts with the React frontend.
2. Frontend sends requests to FastAPI via Axios.
3. FastAPI validates requests using Pydantic DTOs.
4. Services process business logic, interacting with external APIs (OpenAI, Clova, S3) and local repositories.
5. Repositories perform CRUD operations on MySQL via Tortoise ORM.
6. Responses are serialized back to JSON and sent to the frontend.

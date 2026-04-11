# Project Concerns & Risks

## Technical Concerns
- **ORM Transition**: Codebase contains references to both Tortoise ORM and SQLAlchemy (`backend/pyproject.toml`). Consistency is needed.
- **Mock Data**: `ocr_service.py` currently uses hardcoded mock data for parsing Clova OCR results. This needs a robust parser.
- **Dependency Versioning**: some dependencies like `bcrypt` have specific version constraints (`<=4.0.1`) that might conflict with newer packages.

## Performance
- **AI Processing Latency**: OpenAI and Clova OCR calls are synchronous or high-latency. Ensure they don't block main API threads (using `async` helps, but task queues like Redis/Celery might be needed for heavy loads).
- **Large Dataset Seeding**: The drug database seeding script needs careful management to handle large datasets efficiently.

## Development Workflow
- **Database Synchronization**: Strict adherence to the `aerich` upgrade workflow is required to avoid schema inconsistencies among team members.
- **Frontend-Backend Integration**: Ensure DTOs and API definitions are synchronized to prevent runtime errors.

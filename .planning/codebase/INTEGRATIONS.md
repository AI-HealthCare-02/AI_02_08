# External Integrations

## Core Services
- **OpenAI API**: Used for generating AI-based reports and clinical insights.
- **Naver Clova OCR**: Integrated for prescription analysis and text extraction.
- **AWS S3**: Utilized for file storage (e.g., uploading prescription images) via `aioboto3`.

## Database Services
- **MySQL**: Primary relational database for user data, medications, and reports.
- **Redis**: Used for caching and potentially as a message broker for task queues.

## Communication
- **FastAPI-Mail**: Used for sending system emails/notifications.

# Coding Conventions

## General
- **Naming**: Use `snake_case` for Python and `camelCase` or `PascalCase` (components) for TypeScript/React.
- **Documentation**: All public functions and classes should have docstrings (Python) or JSDoc (TS/JS).
- **Korean Language**: All documentation and descriptions must be in Korean per project rules.

## Python (Backend)
- **Formatting**: Use `ruff format`.
- **Linting**: Use `ruff check`.
- **Type Hinting**: Mandatory for all function signatures and complex variables.
- **ASync**: Use `async`/`await` for all I/O bound operations.
- **Error Handling**: Use custom exception classes and FastAPI exception handlers.

## TypeScript/React (Frontend)
- **Hooks**: Use functional components and hooks exclusively.
- **Types**: Define interfaces or types for all API responses and component props.
- **Components**: Group related styles and tests with components.
- **State**: Prefer local state and context over heavy global state libraries.

## Database
- **Migrations**: Always use `uv run aerich migrate` and `upgrade`. Never modify `migrations` files manually.
- **Models**: Do not modify models via external tools; only use code-first updates in `app/models`.
